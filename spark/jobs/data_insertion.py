import sys, os
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent

if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

from pyspark.sql import DataFrame

# local imports
from utils.sparkUtils import get_spark_session, get_logger, read_data
from settings import settings


min_folder='derived'
clean_folder='cleaned'

# connection
# table_name='fitness.fact_daily_workouts'
table_name = f"{settings.SCHEMA_NAME}.{settings.TABLE_NAME}"

def main(spark)-> DataFrame:
    df = read_data(
        bucket_name=settings.BUCKET_NAME,
        folder=clean_folder,
        min_folder=min_folder,
        spark=spark
    )
    # df.printSchema()
    postgres_url = f"jdbc:postgresql://{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
    (
        df.write 
        .format("jdbc") 
        .option("url", postgres_url)
        .option("dbtable", table_name) 
        .option("user", settings.POSTGRES_USER) 
        .option("password", settings.POSTGRES_PASSWORD) 
        .mode("overwrite") 
        .save()
    )




if __name__=='__main__':
    spark = get_spark_session(appname=settings.APP_NAME, use_minio=True)
    main(spark=spark)
    spark.stop()