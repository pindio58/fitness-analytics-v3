# from airflow.sdk import task, dag
# from airflow.providers.standard.operators.empty import EmptyOperator
# from airflow.providers.standard.operators.trigger_dagrun import TriggerDagRunOperator


# import os
# from pathlib import Path
# import json

# from utils.constants import AIRFLOW_CONN_MINIO
# from utils.commonUtils import get_logger, upload_file_to_minio
# from utils.defaults import (
#     DEFAULT_ARGS,
#     CATCHUP,
#     SCHEDULE,
#     START_DATE,
#     IS_PAUSED_UPON_CREATION,
#     PER_PAGE,
#     PREFIX_BRONZE,
# )


# from strava_module.loader import fetch_activities_to_file, fetch_athlete, fetch_gear

# logger = get_logger(__name__)

# athlete_id = os.getenv("athlete_id")

# # ============================================
# #                   define tasks            ==
# # ============================================


# @task
# def fetch_files(per_page):
#     files = [str(filename) for filename in fetch_activities_to_file(per_page=per_page)]
#     logger.info(f"Fetched {len(files)} activity files")
#     return files


# @task
# def fetch_athlete_files():
#     files = [str(filename) for filename in fetch_athlete()]
#     logger.info(f"Fetched {len(files)} athlete files")
#     return files


# @task
# def extract_gear_ids(files):
#     gear_ids = set()

#     for file in files:
#         with open(file, "r") as f:
#             activities = json.load(f)

#             for activity in activities:
#                 gid = activity.get("gear_id")
#                 if gid:
#                     gear_ids.add(gid)
#     gear_ids = list(gear_ids)
#     logger.info(f"Extracted {len(gear_ids)} gear IDs from files")
#     return gear_ids


# @task
# def fetch_gear_files(gear_ids):
#     files = []
#     for gid in gear_ids:
#         for filename in fetch_gear(gear_id=gid):
#             files.append(str(filename))
#     return files


# @task
# def upload_file(filename, layer, table):
#     filename = Path(filename)
#     bucket_name = os.environ["BUCKET_NAME"]
#     key = f"{layer.rstrip('/')}/{table}/{filename.name}"
#     logger.info(f"Uploading {filename.name} to s3://{bucket_name}/{key}")
#     upload_file_to_minio(
#         aws_conn_id=AIRFLOW_CONN_MINIO,
#         filename=filename,
#         bucket_name=bucket_name,
#         key=key,
#     )


# # ============================================
# #                   DAG                     ==
# # ============================================


# @dag(
#     default_args=DEFAULT_ARGS,
#     catchup=CATCHUP,
#     dag_display_name="fetch-activities",
#     dag_id="fetch-activities",
#     schedule=SCHEDULE,
#     start_date=START_DATE,
#     is_paused_upon_creation=IS_PAUSED_UPON_CREATION,
# )
# def main():
#     start = EmptyOperator(task_id="start")
#     files = fetch_files(per_page=PER_PAGE)
#     athlete_files = fetch_athlete_files()

#     gear_ids = extract_gear_ids(files=files)
#     gear_files = fetch_gear_files(gear_ids=gear_ids)

#     uploads = upload_file.override(task_id="upload_activities").expand(
#         filename=files, layer=[PREFIX_BRONZE], table=["activities"]
#     )
#     athlete_uploads = upload_file.override(task_id="upload_athlete").expand(
#         filename=athlete_files, layer=[PREFIX_BRONZE], table=["athlete"]
#     )
#     gear_uploads = upload_file.override(task_id="upload_gear").expand(
#         filename=gear_files, layer=[PREFIX_BRONZE], table=["gears"]
#     )
#     end = EmptyOperator(task_id="end")

#     trigger_dag_2 = TriggerDagRunOperator(
#         trigger_dag_id="sparkProcessing",
#         wait_for_completion=False,
#         task_id="trigger_dag2",
#     )

#     start >> files >> uploads >> end
#     start >> athlete_files >> athlete_uploads >> end

#     files >> gear_ids >> gear_files >> gear_uploads >> end

#     end >> trigger_dag_2


# main()

from airflow.sdk import dag, task
from utils.constants import AIRFLOW_CONN_MINIO


@task
def test():
    print("OK")


@dag(schedule=None, start_date=None, catchup=False)
def test_dag():
    test()


test_dag()
