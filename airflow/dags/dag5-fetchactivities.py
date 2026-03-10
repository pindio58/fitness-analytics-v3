from airflow.providers.standard.operators.empty import EmptyOperator
from airflow.sdk import (
    dag,
    task
)

from pathlib import Path
import os
from datetime import datetime

from strava_module.loader import load_activities

athlete_id= os.getenv('athlete_id')

default_args={'owner':'pindio58',
              'depends_on_past':False,
              'retries':0,
              'email_on_failure':False}


@task
def ingest():
    return load_activities()


@dag(default_args=default_args,
     catchup=False,
     dag_display_name='fetchAthlete',
      dag_id='fetchAthlete',
      schedule=None,
      start_date=datetime(2025,12,1),
      is_paused_upon_creation=False)
def etl():
    start = EmptyOperator(task_id='start')
    athlete = ingest()
    end = EmptyOperator(task_id='end')

    start >> athlete_id >> end

etl()