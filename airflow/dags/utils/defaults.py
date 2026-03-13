from datetime import datetime, timedelta
from pathlib import Path
import os


DEFAULT_ARGS = {
    "owner": "pindio58",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(seconds=30),
    "email_on_failure": False,
}

CATCHUP = False
SCHEDULE = None
START_DATE = datetime(2025, 12, 1)
IS_PAUSED_UPON_CREATION = False
BASE_DIR = Path(os.environ['AIRFLOW_HOME'])
PER_PAGE=200
PREFIX_RAW="raw"