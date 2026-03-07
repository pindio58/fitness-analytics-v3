#fro airflow imports
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from airflow.providers.standard.operators.empty import EmptyOperator
from airflow.sdk import dag
from airflow.providers.standard.operators.trigger_dagrun import TriggerDagRunOperator

# import python modules
from datetime import datetime

from  settings import settings

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
        params={'schema': settings.SCHEMA_NAME, 'fitness_table': settings.FITNESS_TABLE_NAME, 'token_table': settings.TOKEN_TABLE_NAME},
        conn_id=settings.AIRFLOW_CONN_POSTGRES,
        database=settings.POSTGRES_DATABASE
     )
    end = EmptyOperator(task_id='end')

    trigger_dag_2 = TriggerDagRunOperator(trigger_dag_id='fitness-analytics',
                                          wait_for_completion=False,
                                          task_id='trigger_dag2')

    start >> create_table_task >> end >> trigger_dag_2

etl()