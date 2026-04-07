from pyspark.sql import SparkSession
from pyspark.sql import functions as F

import sys, os
from pathlib import Path

BASE_DIR = Path(os.environ["SPARK_HOME"])

if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

# local imports
from utils.sparkUtils import get_spark_session, write_data, read_remote_data, get_logger
from settings import settings

logger = get_logger(__name__)

# spark imports
from pyspark.sql import functions as F
from pyspark.sql.window import Window
from pyspark.sql import DataFrame
from pyspark.sql.types import (
    StringType,
    StructField,
    DoubleType,
    StructType,
    BooleanType,
    LongType,
)
from pyspark.sql import SparkSession

# define gear schema
gear_schema = StructType(
    [
        StructField("id", StringType(), True),
        StructField("primary", BooleanType(), True),
        StructField("name", StringType(), True),
        StructField("nickname", StringType(), True),
        StructField("resource_state", LongType(), True),
        StructField("retired", BooleanType(), True),
        StructField("distance", DoubleType(), True),
        StructField("converted_distance", DoubleType(), True),
        StructField("brand_name", StringType(), True),
        StructField("model_name", StringType(), True),
        StructField("description", StringType(), True),
        StructField("weight", DoubleType(), True),
        StructField("frame_type", LongType(), True),
        StructField("notification_distance", LongType(), True),
    ]
)


def main(spark: SparkSession):
    logger.info("Starting athlete and activities processing job")

    # -----------------------------
    # Load Data (Bronze Layer)
    # -----------------------------
    activities_df = read_remote_data(
        spark=spark,
        bucket_name=settings.BUCKET_NAME,
        layer=settings.BRONZE,
        table=settings.ACTIVITIES,
        format="json",
    )

    athlete_df = read_remote_data(
        spark=spark,
        bucket_name=settings.BUCKET_NAME,
        layer=settings.BRONZE,
        table=settings.ATHLETE,
        format="json",
    )

    gear_df = read_remote_data(
        spark=spark,
        bucket_name=settings.BUCKET_NAME,
        layer=settings.BRONZE,
        table=settings.GEAR,
        format="json",
        schema=gear_schema,
    )

    # -----------------------------
    # 3. Clean Activities (Silver)
    # -----------------------------
    activities_df = (
        activities_df.withColumn("athlete_id", F.col("athlete.id"))
        .withColumn("activity_id", F.col("id"))
        .withColumn("summary_polyline", F.col("map.summary_polyline"))
        .withColumn("start_lat", F.get(F.col("start_latlng"), 0))
        .withColumn("start_lng", F.get(F.col("start_latlng"), 1))
        .withColumn("end_lat", F.get(F.col("end_latlng"), 0))
        .withColumn("end_lng", F.get(F.col("end_latlng"), 1))
        .withColumn("has_gps", F.col("gear_id").isNotNull())
        .withColumn("start_date", F.to_timestamp("start_date"))
        .withColumn("start_date_local", F.to_timestamp("start_date_local"))
        .withColumn("distance_km", F.col("distance") / 1000)
        .withColumn("moving_time_min", F.col("moving_time") / 60)
        .withColumn("elapsed_time_min", F.col("elapsed_time") / 60)
        .withColumn("avg_speed_kmh", F.col("average_speed") * 3.6)
        .withColumn("max_speed_kmh", F.col("max_speed") * 3.6)
        .withColumn("elevation_gain_km", F.col("total_elevation_gain") / 1000)
        .withColumn("year", F.year("start_date"))
        .withColumn("month", F.month("start_date"))
        .withColumn("week", F.weekofyear("start_date"))
        .withColumn("day", F.to_date("start_date"))
        .drop("athlete", "map", "start_latlng", "end_latlng")
    )

    # Remove garbage
    activities_df = activities_df.filter(F.col("distance_km") > 0).dropDuplicates(
        ["activity_id"]
    )

    # -----------------------------
    # 4. Derived Metrics
    # -----------------------------
    activities_df = (
        activities_df.withColumn(
            "pace_min_per_km",
            F.when(
                F.col("distance_km") > 0,
                F.col("moving_time_min") / F.col("distance_km"),
            ),
        )
        .withColumn("is_long_activity", F.col("distance_km") >= 10)
        .withColumn("is_fast_activity", F.col("avg_speed_kmh") >= 10)
        .withColumn(
            "elevation_per_km",
            F.when(
                F.col("distance_km") > 0,
                F.col("total_elevation_gain") / F.col("distance_km"),
            ),
        )
    )

    # -----------------------------
    # 5. Clean Athlete Data
    # -----------------------------
    athlete_df = (
        athlete_df.withColumnRenamed("id", "athlete_id")
        .withColumn("created_at", F.to_timestamp("created_at"))
        .withColumn("updated_at", F.to_timestamp("updated_at"))
    )

    # -----------------------------
    # 6. Join (Silver Final)
    # -----------------------------
    final_df = activities_df.join(athlete_df, on="athlete_id", how="left")

    # https://www.notion.so/COLUMN_ALREADY_EXISTS-The-column-resource_state-already-exists-Choose-another-name-or-rename-the-e-337e0b22664f8002a3dbf352c436de9b?v=2cde0b22664f8014b67e000cbb85deb6&source=copy_link
    final_df = final_df.drop("resource_state")

    ## clean gear df
    gear_df = gear_df.select(
        F.col("id").alias("gear_id"),
        F.col("name").alias("gear_name"),
        "brand_name",
        "model_name",
        F.col("distance").alias("gear_distance"),
    )
    gear_df = gear_df.withColumn(
        "gear_type", F.when(F.col("gear_id").startswith("b"), "bike").otherwise("shoes")
    )

    # join with activities
    final_df = final_df.join(gear_df, on="gear_id", how="left")

    # -----------------------------
    # 7. GOLD LAYER (Aggregations)
    # -----------------------------

    # Daily Summary
    daily_df = final_df.groupBy("day").agg(
        F.count("*").alias("num_activities"),
        F.sum("distance_km").alias("total_distance_km"),
        F.sum("moving_time_min").alias("total_time_min"),
        F.avg("avg_speed_kmh").alias("avg_speed_kmh"),
        F.avg("pace_min_per_km").alias("avg_pace"),
    )

    # Monthly Summary
    monthly_df = final_df.groupBy("year", "month").agg(
        F.sum("distance_km").alias("total_distance_km"),
        F.count("*").alias("num_activities"),
        F.avg("pace_min_per_km").alias("avg_pace"),
        F.sum("total_elevation_gain").alias("total_elevation"),
    )

    # Activity Type Summary
    type_df = final_df.groupBy("sport_type").agg(
        F.count("*").alias("count"),
        F.sum("distance_km").alias("total_distance_km"),
        F.avg("avg_speed_kmh").alias("avg_speed"),
    )

    # Personal Records
    pr_df = final_df.agg(
        F.max("distance_km").alias("longest_distance"),
        F.max("avg_speed_kmh").alias("max_speed"),
        F.min("pace_min_per_km").alias("best_pace"),
        F.max("total_elevation_gain").alias("max_elevation"),
    )

    # Silver
    write_data(
        df=final_df,
        bucket_name=settings.BUCKET_NAME,
        layer=settings.SILVER,
        table="activities_enriched",
    )

    # -----------------------------
    # 8. Write Outputs
    # -----------------------------

    write_data(
        df=final_df,
        bucket_name=settings.BUCKET_NAME,
        layer=settings.SILVER,
        table="activities_enriched",
    )

    write_data(
        df=daily_df,
        bucket_name=settings.BUCKET_NAME,
        layer=settings.GOLD,
        table="daily_summary",
    )

    write_data(
        df=monthly_df,
        bucket_name=settings.BUCKET_NAME,
        layer=settings.GOLD,
        table="monthly_summary",
    )

    write_data(
        df=type_df,
        bucket_name=settings.BUCKET_NAME,
        layer=settings.GOLD,
        table="type_summary",
    )

    write_data(
        df=pr_df,
        bucket_name=settings.BUCKET_NAME,
        layer=settings.GOLD,
        table="personal_records",
    )

    logger.info("Completed athlete and activities processing job")


if __name__ == "__main__":
    # 1. Spark Session
    spark = get_spark_session(appname=settings.APP_NAME, use_minio=True)
    main(spark=spark)
    spark.stop()
