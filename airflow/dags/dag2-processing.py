from airflow.sdk import task, dag
from airflow.providers.standard.operators.empty import EmptyOperator
from airflow.providers.cncf.kubernetes.operators.spark_kubernetes import SparkKubernetesOperator


from datetime import datetime
import os,sys
from pathlib import Path

BASE_DIR = os.environ['AIRFLOW_HOME']

from utils.commonUtils import get_logger, upload_file_to_minio


data_dir = BASE_DIR / "data" 
filename = str(data_dir / "synthetic_fitness_6_months.csv")

#============================================ define tasks ============================================


@task
def file_upload(filename, prefix='raw'):
    filename= Path(filename)
    bucket_name=os.environ['BUCKET_NAME']
    key = f"{prefix.rstrip('/')}/{filename.name}" # filename.name keeps only filename; prefix.rstrip('/') avoids raw//file.csv 
    upload_file_to_minio(aws_conn_id='minio_default',
                         filename=filename,
                         bucket_name=bucket_name,
                         key=key)



#======================================================================================================


default_args={'owner':'pindio58',
              'depends_on_past':False,
              'retries':0,
              'email_on_failure':False}



@dag(default_args=default_args,
     catchup=False,
     dag_display_name='fitness-analytics',
      dag_id='fitness-analytics',
      schedule=None,
      start_date=datetime(2025,12,1),
      is_paused_upon_creation=True)

def etl():
    start = EmptyOperator(task_id='start')
    end = EmptyOperator(task_id='end')
    upload = file_upload(filename=filename, prefix='raw')

    spark_test= SparkKubernetesOperator(
        task_id='cleansing-data',
        do_xcom_push=False,
        namespace='fitness-analytics-namespace',
        application_file='spark/sparkapplicationCleaning.yml',
        kubernetes_conn_id='spark_kubernetes_default',
        delete_on_termination=True
    )

    start >> upload >> spark_test >> end

etl()