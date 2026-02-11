"""
MinIO Document Storage Service

Production-grade MinIO (S3-compatible) storage implementation for on-premise deployments.
Implements the DocumentStorageServiceInterface for seamless provider switching.
"""
import asyncio
import logging
import os
from typing import IO
from io import BytesIO

from minio import Minio
from minio.error import S3Error
from fastapi import UploadFile

from app.core.config import settings
from app.services.interfaces.document_storage_service_interface import DocumentStorageServiceInterface
from app.schema.response.meta import ResponseMeta
from app.utils.exception_utils import BadRequestException, NotFoundException


logger = logging.getLogger(__name__)


class MinioDocumentStorageService(DocumentStorageServiceInterface):
    """MinIO implementation of document storage service for on-premise S3-compatible storage."""
    
    def __init__(self):
        """Initialize MinIO client with credentials from settings."""
        if not settings.MINIO_ENDPOINT:
            raise ValueError("MINIO_ENDPOINT is required when using MinIO storage provider")
        if not settings.MINIO_ACCESS_KEY:
            raise ValueError("MINIO_ACCESS_KEY is required when using MinIO storage provider")
        if not settings.MINIO_SECRET_KEY:
            raise ValueError("MINIO_SECRET_KEY is required when using MinIO storage provider")
        if not settings.MINIO_BUCKET_NAME:
            raise ValueError("MINIO_BUCKET_NAME is required when using MinIO storage provider")
        
        self.minio_client = Minio(
            endpoint=settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_USE_SSL
        )
        self.bucket_name = settings.MINIO_BUCKET_NAME
        self.cdn_url = settings.MINIO_CDN_URL
        self.endpoint = settings.MINIO_ENDPOINT
        self.use_ssl = settings.MINIO_USE_SSL
        
        # Ensure bucket exists (create if not)
        self._ensure_bucket_exists()
    
    def _ensure_bucket_exists(self) -> None:
        """Create bucket if it doesn't exist."""
        try:
            if not self.minio_client.bucket_exists(self.bucket_name):
                self.minio_client.make_bucket(self.bucket_name)
                logger.info(f"Created MinIO bucket: {self.bucket_name}")
        except S3Error as e:
            logger.error(f"Error checking/creating bucket: {e}")
            # Don't raise - bucket might already exist or user might not have create permissions
    
    async def upload_file(
        self,
        file: UploadFile,
        file_path: str,
        allowed_extensions: list[str]
    ) -> str | None:
        """
        Upload a file to MinIO.
        
        Args:
            file: The file to upload
            file_path: The destination path/key in MinIO
            allowed_extensions: List of allowed file extensions (e.g., ['.jpg', '.png'])
            
        Returns:
            The public URL of the uploaded file, or None if validation fails
        """
        # Validate file is not null
        if file is None:
            raise BadRequestException("file", "No file provided")
        
        # Validate file has a filename
        if not file.filename:
            raise BadRequestException("file", "File must have a filename")
        
        # Get file extension
        _, file_extension = os.path.splitext(file.filename)
        
        # Validate file has an extension
        if not file_extension:
            raise BadRequestException("file", "File must have an extension")
        
        # Normalize extension to lowercase
        file_extension = file_extension.lower()
        
        # Normalize allowed extensions to lowercase
        normalized_allowed_extensions = [ext.lower() for ext in allowed_extensions]
        
        # Validate extension is in allowed list
        if file_extension not in normalized_allowed_extensions:
            raise BadRequestException(
                "file", 
                f"File extension '{file_extension}' is not allowed. Allowed extensions: {', '.join(allowed_extensions)}"
            )
        
        try:
            # Read file content
            file_content = await file.read()
            file_stream = BytesIO(file_content)
            file_size = len(file_content)
            
            # Determine content type
            content_type = file.content_type or "application/octet-stream"
            
            # Upload to MinIO using asyncio.to_thread for async compatibility
            await asyncio.to_thread(
                self.minio_client.put_object,
                self.bucket_name,
                file_path,
                file_stream,
                file_size,
                content_type=content_type
            )
            
            # Reset file position for potential reuse
            await file.seek(0)
            
            # Return CDN URL or MinIO bucket URL
            return self._build_file_url(file_path)
            
        except S3Error as e:
            logger.error(f"Error uploading file to MinIO: {e}")
            raise BadRequestException("file", f"Failed to upload file to MinIO: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error during file upload: {e}")
            raise BadRequestException("file", f"Unexpected error during file upload: {str(e)}")
    
    async def upload_stream(
        self,
        stream: IO[bytes],
        file_path: str,
        content_type: str
    ) -> str | None:
        """
        Upload a file from a stream to MinIO.
        
        Args:
            stream: The byte stream to upload
            file_path: The destination path/key in MinIO
            content_type: The MIME type of the file
            
        Returns:
            The public URL of the uploaded file, or None if upload fails
        """
        # Validate stream is not null
        if stream is None:
            raise BadRequestException("stream", "No stream provided")
        
        try:
            # Read stream content to get size (MinIO requires content length)
            stream.seek(0)
            content = stream.read()
            file_size = len(content)
            file_stream = BytesIO(content)
            
            # Upload to MinIO using asyncio.to_thread for async compatibility
            await asyncio.to_thread(
                self.minio_client.put_object,
                self.bucket_name,
                file_path,
                file_stream,
                file_size,
                content_type=content_type
            )
            
            # Return CDN URL or MinIO bucket URL
            return self._build_file_url(file_path)
            
        except S3Error as e:
            logger.error(f"Error uploading stream to MinIO: {e}")
            raise BadRequestException("stream", f"Failed to upload stream to MinIO: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error during stream upload: {e}")
            raise BadRequestException("stream", f"Unexpected error during stream upload: {str(e)}")
    
    async def remove(
        self,
        key: str
    ) -> ResponseMeta:
        """
        Remove a file from MinIO.
        
        Args:
            key: The file key/path or full URL
            
        Returns:
            ResponseMeta with success or error message
        """
        try:
            # Extract the actual key from potential URL
            key = self._extract_key(key)
            
            # Validate key is not empty after stripping
            if not key:
                return ResponseMeta(message="Invalid file key")
            
            # Check if object exists before deleting
            try:
                await asyncio.to_thread(
                    self.minio_client.stat_object,
                    self.bucket_name,
                    key
                )
            except S3Error as e:
                if e.code == "NoSuchKey":
                    return ResponseMeta(message="File not found")
                raise
            
            # Delete object from MinIO using asyncio.to_thread for async compatibility
            await asyncio.to_thread(
                self.minio_client.remove_object,
                self.bucket_name,
                key
            )
            
            return ResponseMeta(message="File deleted successfully")
            
        except S3Error as e:
            error_message = f"Error deleting file from MinIO: {str(e)}"
            logger.error(error_message)
            return ResponseMeta(message=error_message)
        except Exception as e:
            error_message = f"Unexpected error during file deletion: {str(e)}"
            logger.error(error_message)
            return ResponseMeta(message=error_message)
    
    async def copy(
        self,
        source_key: str,
        destination_key: str
    ) -> str | None:
        """
        Copy a file from one location to another within MinIO.
        
        Args:
            source_key: The source file key/path or full URL
            destination_key: The destination file key/path
            
        Returns:
            The public URL of the copied file, or None if copy failed
        """
        from minio.commonconfig import CopySource
        
        try:
            # Extract the actual key from potential URL
            source_key = self._extract_key(source_key)
            
            # Validate keys are not empty
            if not source_key or not destination_key:
                raise BadRequestException("file_key", "Source key and destination key are required")
            
            # Check if source object exists
            try:
                await asyncio.to_thread(
                    self.minio_client.stat_object,
                    self.bucket_name,
                    source_key
                )
            except S3Error as e:
                if e.code == "NoSuchKey":
                    raise NotFoundException("source_key", f"Source file not found: {source_key}")
                raise
            
            # Copy object in MinIO using asyncio.to_thread for async compatibility
            copy_source = CopySource(self.bucket_name, source_key)
            
            await asyncio.to_thread(
                self.minio_client.copy_object,
                self.bucket_name,
                destination_key,
                copy_source
            )
            
            # Return URL of the copied file
            return self._build_file_url(destination_key)
            
        except S3Error as e:
            logger.error(f"Error copying file in MinIO: {e}")
            raise BadRequestException("copy", f"Failed to copy file in MinIO: {str(e)}")
        except (BadRequestException, NotFoundException):
            raise
        except Exception as e:
            logger.error(f"Unexpected error during file copy: {e}")
            raise BadRequestException("copy", f"Unexpected error during file copy: {str(e)}")
    
    async def move(
        self,
        source_key: str,
        destination_key: str
    ) -> str | None:
        """
        Move a file from one location to another within MinIO.
        This is implemented as copy + delete.
        
        Args:
            source_key: The source file key/path or full URL
            destination_key: The destination file key/path
            
        Returns:
            The public URL of the moved file, or None if move failed
        """
        try:
            # First, copy the file
            copied_url = await self.copy(source_key, destination_key)
            
            # Extract the key for deletion
            stripped_source_key = self._extract_key(source_key)
            
            # Then, delete the source file
            await asyncio.to_thread(
                self.minio_client.remove_object,
                self.bucket_name,
                stripped_source_key
            )
            
            return copied_url
            
        except (BadRequestException, NotFoundException):
            raise
        except S3Error as e:
            logger.error(f"Error moving file in MinIO: {e}")
            raise BadRequestException("move", f"Failed to move file in MinIO: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error during file move: {e}")
            raise BadRequestException("move", f"Unexpected error during file move: {str(e)}")
    
    def _build_file_url(self, file_path: str) -> str:
        """
        Build the file URL using CDN URL if available, otherwise generate a presigned URL.
        
        Args:
            file_path: The file path/key in MinIO
            
        Returns:
            The complete URL to access the file (CDN URL or presigned URL)
        """
        from datetime import timedelta
        
        if self.cdn_url:
            return f"{self.cdn_url.rstrip('/')}/{file_path}"
        else:
            # Generate presigned URL for secure, time-limited access
            try:
                presigned_url = self.minio_client.presigned_get_object(
                    bucket_name=self.bucket_name,
                    object_name=file_path,
                    expires=timedelta(minutes=settings.PRESIGNED_URL_EXPIRE_MINUTES)
                )
                return presigned_url
            except S3Error as e:
                logger.error(f"Error generating presigned URL: {e}")
                # Fallback to standard MinIO URL (may not be publicly accessible)
                protocol = "https" if self.use_ssl else "http"
                return f"{protocol}://{self.endpoint}/{self.bucket_name}/{file_path}"
    
    def _extract_key(self, key: str) -> str:
        """
        Extract the actual object key from a URL or path.
        
        Handles:
            - CDN URLs: https://cdn.example.com/path/to/file.jpg
            - MinIO URLs: http://localhost:9000/bucket/path/to/file.jpg
            - Raw keys: path/to/file.jpg
        
        Args:
            key: The file key, path, or full URL
            
        Returns:
            The extracted object key
        """
        # Strip CDN URL from key if present
        if self.cdn_url and key.startswith(self.cdn_url):
            key = key.replace(self.cdn_url.rstrip('/'), "").lstrip("/")
            return key
        
        # Strip MinIO bucket URL from key if present
        protocol = "https" if self.use_ssl else "http"
        bucket_url = f"{protocol}://{self.endpoint}/{self.bucket_name}/"
        if key.startswith(bucket_url):
            key = key.replace(bucket_url, "")
            return key
        
        # Also handle without trailing slash
        bucket_url_no_slash = f"{protocol}://{self.endpoint}/{self.bucket_name}"
        if key.startswith(bucket_url_no_slash):
            key = key.replace(bucket_url_no_slash, "").lstrip("/")
            return key
        
        return key
