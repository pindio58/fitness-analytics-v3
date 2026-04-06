import sys, os
from pathlib import Path

from pyspark.sql import DataFrame

# local imports
from utils.sparkUtils import get_spark_session, get_logger, read_remote_data
from settings import settings


# tables
activities = f"{settings.BRONZE_SCHEMA}.{settings.ACTIVITIES}"
athlete = f"{settings.BRONZE_SCHEMA}.{settings.ATHLETE}"
gears = f"{settings.BRONZE_SCHEMA}.{settings.GEARS}"

activities_enriched = f"{settings.SILVER_SCHEMA}.{settings.ACTIVITIES_ENRICHED}"

daily_summary = f"{settings.GOLD_SCHEMA}.{settings.DAILY_SUMMARY}"
monthly_summary = f"{settings.GOLD_SCHEMA}.{settings.MONTHLY_SUMMARY}"
type_summary = f"{settings.GOLD_SCHEMA}.{settings.TYPE_SUMMARY}"
personal_records = f"{settings.GOLD_SCHEMA}.{settings.PERSONAL_RECORDS}"


# define gear schema
from pyspark.sql.types import (
    StringType,
    StructField,
    DoubleType,
    StructType,
    BooleanType,
    LongType,
)

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


# starting
def main(spark) -> DataFrame:
    postgres_url = f"jdbc:postgresql://{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"

    activities_df = read_remote_data(
        spark=spark,
        bucket_name=settings.BUCKET_NAME,
        layer=settings.BRONZE,
        table=settings.ACTIVITIES_ENRICHED,
        format="parquet",
    )

    (
        activities_df.write.format("jdbc")
        .option("url", postgres_url)
        .option("dbtable", activities_enriched)
        .option("user", settings.POSTGRES_USER)
        .option("password", settings.POSTGRES_PASSWORD)
        .mode("overwrite")
        .save()
    )


if __name__ == "__main__":
    # 1. Spark Session
    spark = get_spark_session(appname=settings.APP_NAME, use_minio=True)
    main(spark=spark)
    spark.stop()
