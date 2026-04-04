# airflow/settings.py
# Centralized Airflow settings for connection names, variables, etc.

# Example Airflow connection names
AIRFLOW_CONN_POSTGRES = "postgres-conn"
AIRFLOW_CONN_MINIO = "minio_default"
AIRFLOW_CONN_SPARK = "spark_kubernetes_default"
POSTGRES_DATABASE = "postgresdb"
SCHEMA_NAME = "fitness"
FITNESS_TABLE_NAME = "fact_daily_workouts"
TOKEN_TABLE_NAME = "strava_tokens"
SILVER_SCHEMA = "silver"
GOLD_SCHEMA = "gold"
BRONZE_SCHEMA = "bronze"
ATHLETE = "athlete"
ACTIVITIES = "activities"
GEARS = "gears"
ACTIVITIES_ENRICHED = "activities_enriched"
DAILY_SUMMARY = "daily_summary"
MONTHLY_SUMMARY = "monthly_summary"
TYPE_SUMMARY = "type_summary"
PERSONAL_RECORDS = "personal_records"
CONFIG_SCHEMA = "config"
