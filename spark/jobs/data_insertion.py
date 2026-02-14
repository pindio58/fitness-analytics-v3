import sys, os
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent

if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

from pyspark.sql import DataFrame

# local imports
from utils.sparkUtils import get_spark_session, get_logger, read_data
from config import BUCKET_NAME, appname


min_folder='derived'
clean_folder='cleaned'

# connection
table_name='fitness.fact_daily_workouts'
POSTGRES_USER = os.environ['POSTGRES_USER']
POSTGRES_PASSWORD = os.environ['POSTGRES_PASSWORD']
POSTGRES_DB= os.environ['POSTGRES_DB']
def main(spark)-> DataFrame:
    df = read_data(
        bucket_name=BUCKET_NAME,
        folder=clean_folder,
        min_folder=min_folder,
        spark=spark
    )
    # df.printSchema()
    (
        df.write 
        .format("jdbc") 
        .option("url", f"jdbc:postgresql://fitness-analytics-postgres-service:5432/{POSTGRES_DB}") #jdbc:postgresql://HOST:PORT/DATABASE
        .option("dbtable", table_name) 
        .option("user", POSTGRES_USER) 
        .option("password", POSTGRES_PASSWORD) 
        .mode("overwrite") 
        .save()
    )




if __name__=='__main__':
    spark = get_spark_session(appname=appname, use_minio=True)
    main(spark=spark)
    spark.stop()