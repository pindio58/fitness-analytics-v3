from .settings import settings

BUCKET_NAME = settings.BUCKET_NAME
MINIO_ENDPOINT = settings.MINIO_ENDPOINT
MINIO_ROOT_USER = settings.MINIO_ROOT_USER
MINIO_ROOT_PASSWORD = settings.MINIO_ROOT_PASSWORD

# legacy name kept for backward compatibility
appname = settings.APP_NAME

SETTINGS = {
	"BUCKET_NAME": BUCKET_NAME,
	"MINIO_ENDPOINT": MINIO_ENDPOINT,
	"MINIO_ROOT_USER": MINIO_ROOT_USER,
	"MINIO_ROOT_PASSWORD": MINIO_ROOT_PASSWORD,
	"appname": appname,
}