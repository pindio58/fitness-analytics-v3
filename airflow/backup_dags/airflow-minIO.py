from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow.sdk import dag, task
from datetime import datetime

filename='/opt/airflow/data/synthetic_fitness_6_months.csv'

@task
def upload_to_minio():
    hook = S3Hook(aws_conn_id='minio_conn')
    hook.load_file(filename=filename,
                   key='csv_files/synthetic_fitness_6_months.csv',
                   bucket_name='fitness-analytics',
                   replace=True)

default_args={'owner':'pindio58',
              'depends_on_past':False,
              'retries':0,
              'email_on_failure':False}

@dag(default_args=default_args,
     catchup=False,
     dag_display_name='s3-integration-v2',
      dag_id='project-fitness-s3',
      schedule=None,
      start_date=datetime(2025,12,1),
      is_paused_upon_creation=True)
def etl_worldbank_population():
    upload = upload_to_minio()
    upload

etl_worldbank_population()


