# BaseSettings reads configuration in this priority order:
# Environment variables (e.g., from Kubernetes env: or envFrom:)
# .env file (if configured)
# Default values in the class
# environment variable names must match the field names in Settings.
    
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

class Settings(BaseSettings):
    client_id: str='1234'
    client_secret: str
    url: str = "https://www.strava.com/oauth/token"
    athlete_id: int = 12345
    AIRFLOW_CONN_POSTGRES='postgres-conn'


    model_config = SettingsConfigDict(
        env_file="/Users/bhupinderjitsingh/airflwstudy/Projects/fitness-analytics-v3/strava_module/.env",
        env_file_encoding="utf-8"
    )


settings = Settings()
