from airflow.sdk import task, dag
from airflow.providers.standard.operators.empty import EmptyOperator
from airflow.providers.cncf.kubernetes.operators.spark_kubernetes import SparkKubernetesOperator


from datetime import datetime
import os
from pathlib import Path

BASE_DIR = Path(os.environ['AIRFLOW_HOME'])

from utils.commonUtils import get_logger


default_args={'owner':'pindio58',
              'depends_on_past':False,
              'retries':0,
              'email_on_failure':False}



@dag(default_args=default_args,
     catchup=False,
     dag_display_name='fitness-analytics-postgres-data-insert',
      dag_id='fitness-analytics-postgres-data-insert',
      schedule=None,
      start_date=datetime(2025,12,1),
      is_paused_upon_creation=True)

def etl():
    start = EmptyOperator(task_id='start')
    end = EmptyOperator(task_id='end')
    

    spark_test= SparkKubernetesOperator(
        task_id='inserting-data',
        do_xcom_push=False,
        namespace='fitness-analytics-namespace',
        application_file='spark/sparkapplicationDataInsertion.yml',
        kubernetes_conn_id='spark_kubernetes_default',
        delete_on_termination=True
    )

    start >> spark_test >> end

etl()