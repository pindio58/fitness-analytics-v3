from pyspark.sql import SparkSession
from pyspark.sql import functions as F

import sys,os
from pathlib import Path
BASE_DIR = Path(os.environ['SPARK_HOME'])

if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

# local imports
from utils.sparkUtils import get_spark_session, get_logger, write_data, read_remote_data
from settings import settings

#spark imports
from pyspark.sql import functions as F
from pyspark.sql.window import Window
from pyspark.sql import DataFrame
from pyspark.sql.types import StringType, StructField, DoubleType, StructType, DateType
from pyspark.sql import SparkSession

#

def main(spark: SparkSession):
    # spark:SparkSession, bucket_name, folder, min_folder, format='parquet'
    activities_df = read_remote_data(
        spark=spark, 
        bucket_name=settings.BUCKET_NAME,
        layer=settings.GOLD,
        table= '',
        format='json'
    )

    pass
    
if __name__=='__main__':
    # 1. Spark Session
    spark = get_spark_session(appname=settings.APP_NAME, use_minio=True)
    main(spark=spark)
    spark.stop()
    
# -----------------------------
# 1. Spark Session
# -----------------------------
spark = SparkSession.builder \
    .appName("Strava Analytics Pipeline") \
    .getOrCreate()

# -----------------------------
# 2. Load Data (Bronze Layer)
# -----------------------------
activities_df = spark.read.parquet("bronze/activities")
athlete_df = spark.read.parquet("bronze/athlete")

# -----------------------------
# 3. Clean Activities (Silver)
# -----------------------------
activities_df = activities_df \
    .withColumn("activity_id", F.col("id")) \
    .withColumn("start_date", F.to_timestamp("start_date")) \
    .withColumn("start_date_local", F.to_timestamp("start_date_local")) \
    .withColumn("distance_km", F.col("distance") / 1000) \
    .withColumn("moving_time_min", F.col("moving_time") / 60) \
    .withColumn("elapsed_time_min", F.col("elapsed_time") / 60) \
    .withColumn("avg_speed_kmh", F.col("average_speed") * 3.6) \
    .withColumn("max_speed_kmh", F.col("max_speed") * 3.6) \
    .withColumn("elevation_gain_km", F.col("total_elevation_gain") / 1000) \
    .withColumn("year", F.year("start_date")) \
    .withColumn("month", F.month("start_date")) \
    .withColumn("week", F.weekofyear("start_date")) \
    .withColumn("day", F.to_date("start_date"))

# Remove garbage
activities_df = activities_df \
    .filter(F.col("distance_km") > 0) \
    .dropDuplicates(["activity_id"])

# -----------------------------
# 4. Derived Metrics
# -----------------------------
activities_df = activities_df \
    .withColumn("pace_min_per_km",
        F.when(F.col("distance_km") > 0,
               F.col("moving_time_min") / F.col("distance_km"))
    ) \
    .withColumn("is_long_activity", F.col("distance_km") >= 10) \
    .withColumn("is_fast_activity", F.col("avg_speed_kmh") >= 10) \
    .withColumn("elevation_per_km",
        F.when(F.col("distance_km") > 0,
               F.col("total_elevation_gain") / F.col("distance_km"))
    )

# -----------------------------
# 5. Clean Athlete Data
# -----------------------------
athlete_df = athlete_df \
    .withColumnRenamed("id", "athlete_id") \
    .withColumn("created_at", F.to_timestamp("created_at")) \
    .withColumn("updated_at", F.to_timestamp("updated_at"))

# -----------------------------
# 6. Join (Silver Final)
# -----------------------------
final_df = activities_df.join(
    athlete_df,
    on="athlete_id",
    how="left"
)

# -----------------------------
# 7. GOLD LAYER (Aggregations)
# -----------------------------

# Daily Summary
daily_df = final_df.groupBy("day").agg(
    F.count("*").alias("num_activities"),
    F.sum("distance_km").alias("total_distance_km"),
    F.sum("moving_time_min").alias("total_time_min"),
    F.avg("avg_speed_kmh").alias("avg_speed_kmh"),
    F.avg("pace_min_per_km").alias("avg_pace")
)

# Monthly Summary
monthly_df = final_df.groupBy("year", "month").agg(
    F.sum("distance_km").alias("total_distance_km"),
    F.count("*").alias("num_activities"),
    F.avg("pace_min_per_km").alias("avg_pace"),
    F.sum("total_elevation_gain").alias("total_elevation")
)

# Activity Type Summary
type_df = final_df.groupBy("sport_type").agg(
    F.count("*").alias("count"),
    F.sum("distance_km").alias("total_distance_km"),
    F.avg("avg_speed_kmh").alias("avg_speed")
)

# Personal Records
pr_df = final_df.agg(
    F.max("distance_km").alias("longest_distance"),
    F.max("avg_speed_kmh").alias("max_speed"),
    F.min("pace_min_per_km").alias("best_pace"),
    F.max("total_elevation_gain").alias("max_elevation")
)

# -----------------------------
# 8. Write Outputs
# -----------------------------

# Silver
final_df.write.mode("overwrite").parquet("silver/activities_enriched")

# Gold
daily_df.write.mode("overwrite").parquet("gold/daily_summary")
monthly_df.write.mode("overwrite").parquet("gold/monthly_summary")
type_df.write.mode("overwrite").parquet("gold/type_summary")
pr_df.write.mode("overwrite").parquet("gold/personal_records")

# -----------------------------
# 9. Done
# -----------------------------
print("✅ Strava pipeline completed successfully")  