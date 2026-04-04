from pathlib import Path

from utils.commonUtils import get_logger

from pyspark.sql import SparkSession
from pyspark.sql import DataFrame
from settings import settings

# ---------- Spark Session ----------


def get_spark_session(appname, use_minio=False):
    logger = get_logger(__name__)
    logger.info(
        f"Building Spark session with app name: {appname}, use_minio: {use_minio}"
    )

    builder = (
        SparkSession.builder.appName(appname)
        .config("spark.driver.extraJavaOptions", "--enable-native-access=ALL-UNNAMED")
        .config("spark.executor.extraJavaOptions", "--enable-native-access=ALL-UNNAMED")
        .config(
            "spark.hadoop.fs.s3a.aws.credentials.provider",
            "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider",
        )
    )

    if use_minio:
        builder = (
            builder.config("spark.hadoop.fs.s3a.endpoint", settings.MINIO_ENDPOINT)
            .config("spark.hadoop.fs.s3a.access.key", settings.MINIO_ROOT_USER)
            .config("spark.hadoop.fs.s3a.secret.key", settings.MINIO_ROOT_PASSWORD)
            .config("spark.hadoop.fs.s3a.path.style.access", "true")
            .config(
                "spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem"
            )
            .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "false")
        )

    spark = builder.getOrCreate()
    logger.info("Spark session built successfully")
    return spark


def read_local_data(spark: SparkSession, source_file: Path, format="csv", schema=None):
    """Read raw CSV data."""
    logger = get_logger(__name__)
    path = str(source_file)
    logger.info(f"Reading raw data from {path}")
    df = spark.read.format(format).schema(schema).option("header", True).load(path)
    logger.info(
        f"Data read successfully — {df.count()} rows, {len(df.columns)} columns"
    )
    return df


def read_remote_data(
    spark: SparkSession, bucket_name, layer, table, format="parquet", schema=None
) -> DataFrame:
    """Read parquet data."""
    source_path = f"s3a://{bucket_name}/{layer}/{table}/"  # fitness-analytics/bronze/activities_page_1.json
    logger = get_logger(__name__)
    logger.info(f"Reading raw data from {source_path}")

    reader = spark.read.format(format)
    if schema is not None:
        reader = reader.schema(schema=schema)

    df = reader.load(source_path)

    logger.info(
        f"Data read successfully — {df.count()} rows, {len(df.columns)} columns"
    )
    return df


def write_data(df, bucket_name, layer, table, partition_by=None):
    """Write data to MinIO in Parquet format."""
    logger = get_logger(__name__)
    target_path = f"s3a://{bucket_name}/{layer}/{table}"
    logger.info(f"Writing data to MinIO with folder name: {target_path}")
    (
        df.write.mode("overwrite")
        .format("parquet")
        .partitionBy(partition_by or [])
        .save(target_path)
    )
    logger.info(f"Data written to {target_path}")


if __name__ == "__main__":
    spark = get_spark_session("test_app", use_minio=True)
