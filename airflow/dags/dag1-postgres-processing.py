#fro airflow imports
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from airflow.providers.standard.operators.empty import EmptyOperator
from airflow.sdk import dag
from airflow.providers.standard.operators.trigger_dagrun import TriggerDagRunOperator

# import python modules
from datetime import datetime

from  settings import AIRFLOW_CONN_POSTGRES, POSTGRES_DATABASE, TABLE_NAME, SCHEMA_NAME

############################  Notes #####################################
## params → available to Jinja templates ({{ params.schema }})        ###
## parameters → passed to the database driver (like %s placeholders)  ###
#########################################################################

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
        params={'schema': SCHEMA_NAME, 'table': TABLE_NAME},
        conn_id=AIRFLOW_CONN_POSTGRES,
        database=POSTGRES_DATABASE
     )
    end = EmptyOperator(task_id='end')

    trigger_dag_2 = TriggerDagRunOperator(trigger_dag_id='fitness-analytics',
                                          wait_for_completion=True,
                                          task_id='trigger_dag2')

    start >> create_table_task >> end >> trigger_dag_2

etl()