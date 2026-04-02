from airflow.sdk import task, dag
from airflow.providers.standard.operators.empty import EmptyOperator
from airflow.providers.cncf.kubernetes.operators.spark_kubernetes import SparkKubernetesOperator


from datetime import datetime
import os
from pathlib import Path
from utils.constants import AIRFLOW_CONN_SPARK

from utils.defaults import ( 
    DEFAULT_ARGS, 
    CATCHUP, 
    SCHEDULE, 
    START_DATE, 
    IS_PAUSED_UPON_CREATION,
    PREFIX_BRONZE
)


@dag(default_args=DEFAULT_ARGS,
     catchup=CATCHUP,
     dag_display_name='sparkProcessing',
      dag_id='sparkProcessing',
      schedule=SCHEDULE,
      start_date=START_DATE,
      is_paused_upon_creation=IS_PAUSED_UPON_CREATION)

def etl():
    start = EmptyOperator(task_id='start')
    end = EmptyOperator(task_id='end')
    

    spark_test= SparkKubernetesOperator(
        task_id='processing-data-using-spark',
        do_xcom_push=False,
        namespace='fitness-analytics-namespace',
        application_file='spark/sparkapplicationDataProcessing.yml',
        kubernetes_conn_id=AIRFLOW_CONN_SPARK,
        delete_on_termination=True
    )

    start >> spark_test >> end

etl()