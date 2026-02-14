from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from airflow.providers.standard.operators.empty import EmptyOperator
from airflow.sdk import dag
from datetime import datetime

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
        conn_id='postgres-conn',
        database='postgresdb'
     )
    end = EmptyOperator(task_id='end')
    start >> create_table_task >> end

etl()