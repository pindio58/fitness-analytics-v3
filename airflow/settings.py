# airflow/settings.py
# Centralized Airflow settings for connection names, variables, etc.

# Example Airflow connection names
AIRFLOW_CONN_POSTGRES = "postgres-conn" 
AIRFLOW_CONN_MINIO = "minio_default"
AIRFLOW_CONN_SPARK = "spark_kubernetes_default"
POSTGRES_DATABASE="postgresdb"
SCHEMA_NAME="fitness" 
FITNESS_TABLE_NAME="fact_daily_workouts"
TOKEN_TABLE_NAME="strava_tokens"
