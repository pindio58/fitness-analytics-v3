from airflow.sdk import task, dag
from airflow.providers.standard.operators.empty import EmptyOperator
from airflow.providers.standard.operators.trigger_dagrun import TriggerDagRunOperator


import os
from pathlib import Path

from utils.constants import AIRFLOW_CONN_MINIO
from utils.commonUtils import get_logger, upload_file_to_minio
from utils.defaults import ( 
    DEFAULT_ARGS, 
    CATCHUP, 
    SCHEDULE, 
    START_DATE, 
    IS_PAUSED_UPON_CREATION,
    PER_PAGE, 
    PREFIX_BRONZE
)


from strava_module.loader import fetch_activities_to_file

athlete_id= os.getenv('athlete_id')

# ============================================
#                   define tasks            ==
# ============================================

@task
def fetch_files(per_page):
    files=[str(filename) for filename in fetch_activities_to_file(per_page=per_page)]
    return files

@task
def upload_file(filename, layer, table):
    filename=Path(filename)
    bucket_name=os.environ['BUCKET_NAME']
    key = f"{layer.rstrip('/')}/{table}/{filename.name}"
    upload_file_to_minio(aws_conn_id=AIRFLOW_CONN_MINIO,
                         filename=filename,
                         bucket_name=bucket_name,
                         key=key)


# ============================================
#                   DAG                     ==
# ============================================


@dag(default_args=DEFAULT_ARGS,
     catchup=CATCHUP,
     dag_display_name='fetch-activities',
      dag_id='fetch-activities',
      schedule=SCHEDULE,
      start_date=START_DATE,
      is_paused_upon_creation=IS_PAUSED_UPON_CREATION)
def main():
    start = EmptyOperator(task_id='start')
    files = fetch_files(per_page=PER_PAGE)
    uploads = upload_file.expand(filename=files,
                                 layer=[PREFIX_BRONZE],
                                 table=['activities'])
    end = EmptyOperator(task_id='end')
    start >> files >> uploads >> end

main()