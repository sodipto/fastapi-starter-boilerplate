from uuid import UUID
import uuid
import os
from fastapi import APIRouter, Depends, UploadFile, File
from dependency_injector.wiring import inject, Provide
from app.core.container import Container
from app.services.interfaces.document_storage_service_interface import DocumentStorageServiceInterface
from app.schema.response.meta import ResponseMeta
from app.utils.exception_utils import BadRequestException

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post("/upload", response_model=dict)
@inject
async def upload_file(
    file: UploadFile = File(...),
    file_storage_service: DocumentStorageServiceInterface = Depends(Provide[Container.file_storage_service])
):
    """
    Upload a file to S3 storage.
    
    Example usage:
    - Allowed extensions: .jpg, .jpeg, .png, .pdf
    - File will be uploaded to 'images/{filename}'
    """
    if not file:
        raise BadRequestException("file", "No file provided")
    
    # Define allowed extensions
    allowed_extensions = [".jpg", ".jpeg", ".png", ".pdf"]
    
    # Generate file path with uuid (filename_uuid.extension)
    filename, file_extension = os.path.splitext(file.filename)
    unique_filename = f"{filename}_{uuid.uuid4()}{file_extension}"
    file_path = f"images/{unique_filename}"
    
    # Upload file
    file_url = await file_storage_service.upload_file(
        file=file,
        file_path=file_path,
        allowed_extensions=allowed_extensions
    )
    
    if file_url is None:
        raise BadRequestException(
            "file",
            "File upload failed. Please check file extension and try again."
        )
    
    return {
        "message": "File uploaded successfully",
        "url": file_url
    }


@router.delete("/delete", response_model=ResponseMeta)
@inject
async def delete_file(
    file_key: str,
    file_storage_service: DocumentStorageServiceInterface = Depends(Provide[Container.file_storage_service])
):
    """
    Delete a file from S3 storage.
    
    Args:
        file_key: The file key or full CDN URL to delete
    """
    if not file_key:
        raise BadRequestException("file_key", "File key is required")
    
    result = await file_storage_service.remove(file_key)
    
    return result
