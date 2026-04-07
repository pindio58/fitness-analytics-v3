from airflow.sdk import dag
from airflow.providers.standard.operators.empty import EmptyOperator
from airflow.providers.cncf.kubernetes.operators.spark_kubernetes import (
    SparkKubernetesOperator,
)
from airflow.providers.standard.operators.trigger_dagrun import TriggerDagRunOperator

from datetime import datetime

from utils.constants import AIRFLOW_CONN_SPARK
from utils.commonUtils import get_logger

logger = get_logger(__name__)

from utils.defaults import (
    DEFAULT_ARGS,
    CATCHUP,
    SCHEDULE,
    START_DATE,
    IS_PAUSED_UPON_CREATION,
)


@dag(
    default_args=DEFAULT_ARGS,
    catchup=CATCHUP,
    dag_display_name="sparkProcessing",
    dag_id="sparkProcessing",
    schedule=SCHEDULE,
    start_date=START_DATE,
    is_paused_upon_creation=IS_PAUSED_UPON_CREATION,
)
def etl():
    logger.info("Starting sparkProcessing DAG definition")
    start = EmptyOperator(task_id="start")
    end = EmptyOperator(task_id="end")

    spark_test = SparkKubernetesOperator(
        task_id="processing-data-using-spark",
        do_xcom_push=False,
        namespace="fitness-analytics-namespace",
        application_file="spark/sparkapplicationDataProcessing.yml",
        kubernetes_conn_id=AIRFLOW_CONN_SPARK,
        delete_on_termination=True,
    )

    trigger_dag_3 = TriggerDagRunOperator(
        trigger_dag_id="create-postgres-tables",
        wait_for_completion=False,
        task_id="trigger_dag3",
    )

    start >> spark_test >> end >> trigger_dag_3


etl()
