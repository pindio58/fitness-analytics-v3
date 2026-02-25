import logging
from pathlib import Path
from datetime import datetime 
from zoneinfo import ZoneInfo
import sys, os
from typing import Optional
from airflow.providers.amazon.aws.hooks.s3 import S3Hook


BASE_DIR = Path(os.environ['AIRFLOW_HOME'])

curr_time = datetime.now(ZoneInfo('Asia/Kolkata')).strftime("%Y%m%d%H%M%S%f")[:-5]
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / f"logs-{curr_time}.log"


def get_logger(name:str):
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    
    logger.setLevel(logging.INFO)
    logger.propagate = False

    # file handler
    file_handler = logging.FileHandler(LOG_FILE, delay=True)
    file_handler.setLevel(logging.DEBUG)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    #format
    formattter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(funcName)s | %(message)s"
    )
    file_handler.setFormatter(formattter)
    console_handler.setFormatter(formattter)

    logger.addHandler(file_handler)
    # logger.addHandler(console_handler)

    return logger

def upload_file_to_minio(
    aws_conn_id: str,
    filename: str,
    key: str,
    bucket_name: str,
    replace: bool = True,
) -> Optional[bool]:
    ''' This is to upload a file to minio'''
    hook = S3Hook(aws_conn_id=aws_conn_id)

    return hook.load_file(
        filename=filename,
        key=key,
        bucket_name=bucket_name,
        replace=replace,
    )

def write_df_to_mino(df, path,bucket_name, partition_by=None):
    logger = get_logger(__name__)
    """Write data to MinIO in Parquet format."""
    logger.info(f"Writing data to MinIO: {path}")
    target_path = f"s3a://{bucket_name}/{path}/"
    (
        df.write.mode("overwrite")
        .format("parquet")
        .partitionBy(partition_by or [])
        .save(target_path)
    )
    logger.info(f"Data written to {target_path}")
