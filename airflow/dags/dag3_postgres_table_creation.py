# fro airflow imports
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from airflow.providers.standard.operators.empty import EmptyOperator
from airflow.sdk import dag
from airflow.providers.standard.operators.trigger_dagrun import TriggerDagRunOperator

# import python modules
from datetime import datetime

from utils.constants import (
    AIRFLOW_CONN_POSTGRES,
    POSTGRES_DATABASE,
    SCHEMA_NAME,
    TOKEN_TABLE_NAME,
    PERSONAL_RECORDS,
    ACTIVITIES_ENRICHED,
    ACTIVITIES,
    TYPE_SUMMARY,
    MONTHLY_SUMMARY,
    DAILY_SUMMARY,
    GEARS,
    GOLD_SCHEMA,
    SILVER_SCHEMA,
    BRONZE_SCHEMA,
    ATHLETE,
    CONFIG_SCHEMA,
)
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
    dag_display_name="create-postgres-tables",
    dag_id="create-postgres-tables",
    schedule=SCHEDULE,
    start_date=START_DATE,
    is_paused_upon_creation=IS_PAUSED_UPON_CREATION,
)
def main():
    start = EmptyOperator(task_id="start")
    create_table_task = SQLExecuteQueryOperator(
        task_id="create-tables",
        sql="ddl/create_objects.sql",
        params={
            "token_table": TOKEN_TABLE_NAME,
            "config_schema": CONFIG_SCHEMA,
            "personal_records": PERSONAL_RECORDS,
            "activities_enriched": ACTIVITIES_ENRICHED,
            "activities": ACTIVITIES,
            "type_summary": TYPE_SUMMARY,
            "monthly_summary": MONTHLY_SUMMARY,
            "daily_summary": DAILY_SUMMARY,
            "gears": GEARS,
            "gold_schema": GOLD_SCHEMA,
            "silver_schema": SILVER_SCHEMA,
            "bronze_schema": BRONZE_SCHEMA,
            "athlete": ATHLETE,
        },
        conn_id=AIRFLOW_CONN_POSTGRES,
        database=POSTGRES_DATABASE,
    )
    end = EmptyOperator(task_id="end")

    trigger_dag_2 = TriggerDagRunOperator(
        trigger_dag_id="fitness-analytics",
        wait_for_completion=False,
        task_id="trigger_dag2",
    )

    start >> create_table_task >> end >> trigger_dag_2


etl()
