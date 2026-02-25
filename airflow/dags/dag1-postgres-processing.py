from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from airflow.providers.standard.operators.empty import EmptyOperator
from airflow.sdk import dag
from datetime import datetime
from  settings import AIRFLOW_CONN_POSTGRES, POSTGRES_DATABASE

@dag(
    dag_id='postgres-operation',
    start_date=datetime(2026, 2, 1),
    schedule=None,
    catchup=False)
def etl():
    start = EmptyOperator(task_id='start')
    create_table_task = SQLExecuteQueryOperator(
        task_id='create-tables',
        sql='ddl/create_tables.sql',
        conn_id=AIRFLOW_CONN_POSTGRES,
        database=POSTGRES_DATABASE
     )
    end = EmptyOperator(task_id='end')
    start >> create_table_task >> end

etl()