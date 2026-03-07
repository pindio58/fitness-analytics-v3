from airflow.providers.standard.operators.empty import EmptyOperator
from airflow.providers.standard.operators.bash import BashOperator
from airflow.sdk import dag, task


from pathlib import Path
import os
from datetime import datetime

BASE_DIR = Path(os.environ['AIRFLOW_HOME'])
file_path = BASE_DIR / "dags"


default_args={'owner':'pindio58',
              'depends_on_past':False,
              'retries':0,
              'email_on_failure':False}



@dag(default_args=default_args,
     catchup=False,
     dag_display_name='refresh-token',
      dag_id='refresh-token',
      schedule=None,
      start_date=datetime(2025,12,1),
      is_paused_upon_creation=False)
def etl():
    start = EmptyOperator(task_id='start')

    refresh_token = BashOperator(
        task_id='refresh_token',
        bash_command='python /opt/airflow/dags/strava_module/auth.py'
    )

    end = EmptyOperator(task_id='end')

    start >> refresh_token >> end

etl()