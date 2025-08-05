from fastapi import APIRouter, File, UploadFile, HTTPException
from app.core.minio_client import minio_client
from app.core.config import settings
import uuid
import io

router = APIRouter()

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        file_id = str(uuid.uuid4())
        file_name = f"{file_id}_{file.filename}"

        content = await file.read()
        stream = io.BytesIO(content)  # 🔧 Wrap bytes in a file-like stream

        minio_client.put_object(
            bucket_name=settings.MINIO_BUCKET,
            object_name=file_name,
            data=stream,  # ✅ file-like object
            length=len(content),
            content_type=file.content_type or "application/octet-stream"
        )

        return {"filename": file_name, "message": "File uploaded successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
