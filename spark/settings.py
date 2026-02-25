from pydantic import BaseSettings


class Settings(BaseSettings):
    BUCKET_NAME: str = "fitness-analytics"
    MINIO_ENDPOINT: str = (
        "http://fitness-analytics-minio-statefulset-0.fitness-analytics-minio-service:9000"
    )
    MINIO_ROOT_USER: str = "postgresadmin"
    MINIO_ROOT_PASSWORD: str = "admin123"

    # application name
    APP_NAME: str = "fitness-analytics"

    # Postgres defaults (can be overridden via env)
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "fitness"
    POSTGRES_HOST: str = "fitness-analytics-postgres-service"
    POSTGRES_PORT: int = 5432

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
