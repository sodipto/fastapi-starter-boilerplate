from uuid import UUID
import uuid
import os
from fastapi import APIRouter, Depends, UploadFile, File, Form
from dependency_injector.wiring import inject, Provide
from app.core.rate_limiting import RateLimit
from app.core.container import Container
from app.services.interfaces.document_storage_service_interface import DocumentStorageServiceInterface
from app.schema.response.meta import ResponseMeta
from app.schema.response.document import DocumentOperationResponse
from app.utils.exception_utils import BadRequestException
from app.core.constants.file_extensions import (
    ALLOWED_IMAGE_EXTENSIONS,
    ALLOWED_VIDEO_EXTENSIONS,
    ALLOWED_EXCEL_EXTENSIONS,
    ALLOWED_DOC_EXTENSIONS,
    ALLOWED_CSV_EXTENSIONS,
    ALLOWED_PDF_EXTENSIONS
)

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post(
    "/upload",
    response_model=DocumentOperationResponse,
    dependencies=[Depends(RateLimit(requests=10, window=60, key_prefix="documents_upload"))]
)
@inject
async def upload_file(
    file: UploadFile = File(...),
    file_path: str = Form(...),
    document_storage_service: DocumentStorageServiceInterface = Depends(Provide[Container.document_storage_service])
):
    """
    Upload a file to S3 storage.
    
    Allowed file types:
    - Images: .jpg, .jpeg, .png, .gif, .bmp, .webp, .svg
    - Videos: .mp4, .avi, .mov, .wmv, .flv, .mkv, .webm
    - Excel: .xls, .xlsx, .xlsm
    - Documents: .doc, .docx
    - CSV: .csv
    - PDF: .pdf
    """
    if not file:
        raise BadRequestException("file", "No file provided")
    
    # Combine all allowed extensions
    allowed_extensions = (
        ALLOWED_IMAGE_EXTENSIONS +
        ALLOWED_VIDEO_EXTENSIONS +
        ALLOWED_EXCEL_EXTENSIONS +
        ALLOWED_DOC_EXTENSIONS +
        ALLOWED_CSV_EXTENSIONS +
        ALLOWED_PDF_EXTENSIONS
    )
    
    # `file_path` is required as a directory/prefix (e.g., "images" or "images/sub").
    provided_path = (file_path or "").strip()
    if not provided_path:
        raise BadRequestException("file_path", "file_path is required")

    # Normalize prefix and append a UUID-based filename to avoid collisions
    provided_path = provided_path.rstrip("/")
    filename, file_extension = os.path.splitext(file.filename)
    unique_filename = f"{filename}_{uuid.uuid4()}{file_extension}"
    final_path = f"{provided_path}/{unique_filename}"

    # Upload file using constructed final_path
    result = await document_storage_service.upload_file(
        file=file,
        file_path=final_path,
        allowed_extensions=allowed_extensions
    )

    url = result.url if result else None
    key = result.key if result and result.key else final_path

    return DocumentOperationResponse(
        message="File uploaded successfully",
        url=url,
        key=key
    )

@router.post(
    "/copy",
    response_model=DocumentOperationResponse,
    dependencies=[Depends(RateLimit(requests=30, window=60, key_prefix="documents_copy"))]
)
@inject
async def copy_file(
    source_key: str,
    destination_key: str,
    document_storage_service: DocumentStorageServiceInterface = Depends(Provide[Container.document_storage_service])
):
    """
    Copy a file from one location to another in S3 storage.
    
    Args:
        source_key: The source file key or full CDN URL
        destination_key: The destination file key/path (e.g., 'images/new_file.jpg')
    """
    if not source_key:
        raise BadRequestException("source_key", "Source key is required")
    
    if not destination_key:
        raise BadRequestException("destination_key", "Destination key is required")
    
    if source_key.lower() == destination_key.lower():
        raise BadRequestException("destination_key", "Destination key must be different from source key")
    
    result = await document_storage_service.copy(source_key, destination_key)
    url = result.url if result else None

    return DocumentOperationResponse(
        message="File copied successfully",
        url=url,
        key=destination_key
    )


@router.post(
    "/move",
    response_model=DocumentOperationResponse,
    dependencies=[Depends(RateLimit(requests=30, window=60, key_prefix="documents_move"))]
)
@inject
async def move_file(
    source_key: str,
    destination_key: str,
    document_storage_service: DocumentStorageServiceInterface = Depends(Provide[Container.document_storage_service])
):
    """
    Move a file from one location to another in S3 storage.
    
    Args:
        source_key: The source file key or full CDN URL
        destination_key: The destination file key/path (e.g., 'images/new_file.jpg')
    """
    if not source_key:
        raise BadRequestException("source_key", "Source key is required")
    
    if not destination_key:
        raise BadRequestException("destination_key", "Destination key is required")
    
    result = await document_storage_service.move(source_key, destination_key)
    url = result.url if result else None

    return DocumentOperationResponse(
        message="File moved successfully",
        url=url,
        key=destination_key
    )

@router.delete(
    "/delete",
    response_model=ResponseMeta,
    dependencies=[Depends(RateLimit(requests=30, window=60, key_prefix="documents_delete"))]
)
@inject
async def delete_file(
    file_key: str,
    document_storage_service: DocumentStorageServiceInterface = Depends(Provide[Container.document_storage_service])
):
    """
    Delete a file from S3 storage.
    
    Args:
        file_key: The file key or full CDN URL to delete
    """
    if not file_key:
        raise BadRequestException("file_key", "File key is required")
    
    result = await document_storage_service.remove(file_key)
    
    return result


