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
    AUTH_URL: str = "https://www.strava.com/oauth/token"
    athlete_id: int = 12345
    AIRFLOW_CONN_POSTGRES: str ='postgres-conn'

    # for local db connection
    pg_host: str="localhost"
    pg_port:str ='5433'
    pg_user:str
    pg_password:str
    pg_db:str="postgresdb"


    # https://www.notion.so/Client-API-handling-31ee0b22664f80b88364ef278bc79ca4?v=2c2e0b22664f80859c7a000cb7523a49&source=copy_link
    BASE_URL: str = "https://www.strava.com/api/v3"
    
    

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )


settings = Settings()
