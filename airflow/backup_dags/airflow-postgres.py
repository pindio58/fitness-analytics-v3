from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from airflow.sdk import dag
from datetime import datetime

@dag(
    dag_id='example_postgres_dag-v2',
    start_date=datetime(2023, 1, 1),
    schedule=None,
    catchup=False)
def perform_analysis():
    create_table_task = SQLExecuteQueryOperator(
        task_id='select_one',
        sql="""
            
            CREATE TABLE IF NOT EXISTS pet2 (
            pet_id SERIAL PRIMARY KEY,
            name VARCHAR NOT NULL,
            pet_type VARCHAR NOT NULL,
            birth_date DATE NOT NULL,
            OWNER VARCHAR NOT NULL);
          
        """,
        conn_id='postgres_conn',
        database='postgresdb'
     )
    create_table_task

perform_analysis()