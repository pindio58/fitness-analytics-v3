# fro airflow imports
from airflow.providers.cncf.kubernetes.operators.spark_kubernetes import (
    SparkKubernetesOperator,
)
from airflow.providers.standard.operators.empty import EmptyOperator
from airflow.sdk import dag
from airflow.providers.standard.operators.trigger_dagrun import TriggerDagRunOperator

from utils.defaults import (
    DEFAULT_ARGS,
    CATCHUP,
    SCHEDULE,
    START_DATE,
    IS_PAUSED_UPON_CREATION,
)
from utils.constants import AIRFLOW_CONN_SPARK


@dag(
    default_args=DEFAULT_ARGS,
    catchup=CATCHUP,
    dag_display_name="insert-data-postgres",
    dag_id="insert-data-postgres",
    schedule=SCHEDULE,
    start_date=START_DATE,
    is_paused_upon_creation=IS_PAUSED_UPON_CREATION,
)
def main():
    start = EmptyOperator(task_id="start")
    end = EmptyOperator(task_id="end")

    spark_test = SparkKubernetesOperator(
        task_id="inserting-data",
        do_xcom_push=False,
        namespace="fitness-analytics-namespace",
        application_file="spark/sparkapplicationDataInsertion.yml",
        kubernetes_conn_id=AIRFLOW_CONN_SPARK,
        delete_on_termination=True,
    )

    start >> spark_test >> end


main()
