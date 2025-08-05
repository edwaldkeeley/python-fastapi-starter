from minio import Minio
from app.core.config import settings

minio_client = Minio(
    endpoint=settings.MINIO_ENDPOINT.replace("http://", "").replace("https://", ""),
    access_key=settings.MINIO_ROOT_USER,
    secret_key=settings.MINIO_ROOT_PASSWORD,
    secure=settings.MINIO_ENDPOINT.startswith("https"),
)

async def ensure_bucket():
    if not minio_client.bucket_exists(settings.MINIO_BUCKET):
        minio_client.make_bucket(settings.MINIO_BUCKET)

