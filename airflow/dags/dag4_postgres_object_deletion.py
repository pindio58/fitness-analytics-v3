# fro airflow imports
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from airflow.providers.standard.operators.empty import EmptyOperator
from airflow.sdk import dag
from airflow.providers.standard.operators.trigger_dagrun import TriggerDagRunOperator


from utils.constants import (
    GOLD_SCHEMA,
    SILVER_SCHEMA,
    BRONZE_SCHEMA,
    CONFIG_SCHEMA,
)
from utils.defaults import (
    AIRFLOW_CONN_POSTGRES,
    POSTGRES_DATABASE,
    DEFAULT_ARGS,
    CATCHUP,
    SCHEDULE,
    START_DATE,
    IS_PAUSED_UPON_CREATION,
)


@dag(
    default_args=DEFAULT_ARGS,
    catchup=CATCHUP,
    dag_display_name="delete-postgres-objects",
    dag_id="delete-postgres-objects",
    schedule=SCHEDULE,
    start_date=START_DATE,
    is_paused_upon_creation=IS_PAUSED_UPON_CREATION,
)
def main():
    start = EmptyOperator(task_id="start")
    create_object_task = SQLExecuteQueryOperator(
        task_id="delete-objects",
        sql="ddl/delete_objects.sql",
        params={
            "config_schema": CONFIG_SCHEMA,
            "gold_schema": GOLD_SCHEMA,
            "silver_schema": SILVER_SCHEMA,
            "bronze_schema": BRONZE_SCHEMA,
        },
        conn_id=AIRFLOW_CONN_POSTGRES,
        database=POSTGRES_DATABASE,
    )
    end = EmptyOperator(task_id="end")

    start >> create_object_task >> end


main()
