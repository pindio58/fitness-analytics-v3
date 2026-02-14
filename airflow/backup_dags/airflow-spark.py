from airflow.providers.cncf.kubernetes.operators.spark_kubernetes import SparkKubernetesOperator

from airflow.sdk import dag
from datetime import datetime

@dag(
    dag_id='airflow-spark-testingv1',
    start_date=datetime(2025, 1, 1),
    schedule=None,
    catchup=False)
def perform_analysis():
    spark_test= SparkKubernetesOperator(
        task_id='submit_spark_jobv1',
        do_xcom_push=False,
        namespace='fitness-analytics-namespace',
        application_file='spark/sparkapplication.yml',
        kubernetes_conn_id='spark_kubernetes_default',
        delete_on_termination=True
    )

    spark_test

perform_analysis()