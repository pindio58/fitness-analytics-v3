import sys,os
from pathlib import Path
# BASE_DIR = Path(__file__).resolve().parent.parent
BASE_DIR = Path(os.environ['SPARK_HOME'])

if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

# local imports
from utils.sparkUtils import get_spark_session, get_logger, read_raw_data, write_data
from settings import settings

#spark imports
from pyspark.sql import functions as F
from pyspark.sql.window import Window
from pyspark.sql import DataFrame
from pyspark.sql.types import StringType, StructField, DoubleType, StructType, DateType
from pyspark.sql import SparkSession


# filepath='/Users/bhupinderjitsingh/airflwstudy/Projects/fitness-analytics-v2/data/synthetic_fitness_6_months.csv'
filepath= BASE_DIR / "data" / settings.FILENAME
clean_folder='cleaned'
error_folder='errors'

# initialize logger
logger = get_logger(settings.APP_NAME)

# define schema and do no use integer type as values has decimals
schema = StructType([
    StructField('date',DateType(),True),
    StructField('day_of_week',StringType(),True),
    StructField('workout_type',StringType(),True),
    StructField('run_distance_km',DoubleType(),True),
    StructField('run_duration_min',DoubleType(),True),
    StructField('avg_pace_min_per_km',DoubleType(),True),
    StructField('boxing_duration_min',DoubleType(),True),
    StructField('skipping_duration_min',DoubleType(),True),
    StructField('desi_workout_duration_min',DoubleType(),True),
    StructField('total_duration_min',DoubleType(),True),
    StructField('avg_heart_rate_bpm',DoubleType(),True),
    StructField('max_heart_rate_bpm',DoubleType(),True),
    StructField('calories_burned',DoubleType(),True),
    StructField('steps',DoubleType())
])

###########################
### data quality checks ###
###########################


# check 1: total_duration_min should ≈ sum of all individual durations
def check_1(df:DataFrame, min_folder='error_1')-> DataFrame:

    df_with_total_duration = (
        df.withColumn('total_duration', 
                        F.round(
                                    (
                                        F.col("boxing_duration_min")+
                                        F.col("skipping_duration_min")+
                                        F.col("desi_workout_duration_min")+
                                        F.col("run_duration_min")
                                    ),1
                                )
                    )
    )
        
    df_with_error = (
        df_with_total_duration.filter(
            F.col("total_duration_min") != F.col("total_duration")  
        )     
    )

    has_errors = df_with_error.limit(1).count()>0

    if has_errors:
        write_data(df=df_with_error,bucket_name=settings.BUCKET_NAME,folder=error_folder,min_folder=min_folder)

    df = (
        df_with_total_duration.filter(
            F.col("total_duration_min")==F.col("total_duration")
        ).drop('total_duration')
    )

    return df



# check 2: avg_pace_min_per_km must be null/zero when run_distance_km = 0
def check_2(df:DataFrame, min_folder='error_2') -> DataFrame:
    violation = (
        (F.col('run_distance_km')==0) &
        ~(
            (F.col('avg_pace_min_per_km').isin (0)) | 
            (F.col('avg_pace_min_per_km').isNull())
        )
    )

    df_with_error = (
        df
        .filter(violation)
    )

    has_errors = df_with_error.limit(1).count()>0
    if has_errors:
        write_data(df=df_with_error,bucket_name=settings.BUCKET_NAME,folder=error_folder,min_folder=min_folder)

    df = (
        df
        .filter(~violation)
    )

    return df


# check3: avg_heart_rate_bpm in [50, 220]
def check_3(df:DataFrame, min_folder='error_3')->DataFrame:
    
    bpm_violation = (
        ~F.col('avg_heart_rate_bpm').between(60, 220) | 
        F.col('avg_heart_rate_bpm').isNull()
    )

    df_with_error = (
        df
        .filter(bpm_violation)
    )

    has_errors = df_with_error.limit(1).count()>0
    if has_errors:
        write_data(df=df_with_error,bucket_name=settings.BUCKET_NAME,folder=error_folder,min_folder=min_folder)
    
    df = (
        df
        .filter(~bpm_violation)
    )

    return df


# check4: max_heart_rate_bpm >= avg_heart_rate_bpm
def check_4(df:DataFrame, min_folder='error_4')->DataFrame:
    
    mhr_violation = (
        F.col("max_heart_rate_bpm").isNotNull() &
        F.col("avg_heart_rate_bpm").isNotNull() &
        (F.col("max_heart_rate_bpm") < F.col("avg_heart_rate_bpm"))
    )
    df_with_error = (
        df
        .filter(mhr_violation)
    )
    
    has_errors = df_with_error.limit(1).count()>0
    if has_errors:
        write_data(df=df_with_error,bucket_name=settings.BUCKET_NAME,folder=error_folder,min_folder=min_folder)
    
    df = (
        df.filter(~mhr_violation)
    )

    return df

# ================================. Derive Columns ======================

def derive_columns(df:DataFrame)-> DataFrame:
    df = (
        df
        .withColumn('did_run', F.col('run_distance_km')>0)
        .withColumn('did_box', F.col('boxing_duration_min')>0)
        .withColumn('did_skip', F.col('skipping_duration_min')>0)
        .withColumn('did_desi_workout', F.col('desi_workout_duration_min')>0)
    )
    
    
    df =(
        df
        .withColumn('calories_per_min',
              F.when(
                  F.lower(F.col('workout_type'))=='rest', 
                  F.lit(0))
              .otherwise(
                  F.col('calories_burned') / F.col('total_duration_min'))
             )
    )
    
    df =(
        df
        .withColumn('calories_per_km',
              F.when(F.col('run_distance_km')>0, 
                     F.col('calories_burned') / F.col('run_distance_km'))
              .otherwise(F.lit(None)))
    )

    df = (
        df
        .withColumn('workout_density',
              F.when(F.col('steps')>0, 
                     F.col('total_duration_min') / (F.col('steps')+1))
              .otherwise(F.lit(None)))
    )
    

    df =(
        df.withColumn('year',
                        F.year(F.col('date')))
            .withColumn('month', 
                        F.month(F.col('date'))) 
            .withColumn('week_of_year', 
                        F.weekofyear(F.col('date')))

    )
    return df

# ======================

def main(spark: SparkSession, post_check_folder='post_check', derived_data='derived'):
    df = read_raw_data(spark=spark, source_file=filepath, schema=schema)    
    checks = {
        1:check_1,
        2:check_2,
        3:check_3,
        4:check_4

    }
    checks_list = list(checks.keys())

    for check in checks_list:
        df = checks[check](df)

    write_data(df=df,bucket_name=settings.BUCKET_NAME,folder=clean_folder,min_folder=post_check_folder)

    df = derive_columns(df=df)
    write_data(df=df,bucket_name=settings.BUCKET_NAME,folder=clean_folder,min_folder=derived_data)


if __name__=='__main__':
    spark = get_spark_session(appname=settings.APP_NAME, use_minio=True)
    main(spark=spark)
    spark.stop()