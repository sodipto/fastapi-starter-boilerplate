import asyncio
import logging
import os
from typing import IO
from io import BytesIO
import boto3
from botocore.exceptions import ClientError
from fastapi import UploadFile
from app.core.config import settings
from app.services.interfaces.document_storage_service_interface import DocumentStorageServiceInterface
from app.schema.response.meta import ResponseMeta
from app.utils.exception_utils import BadRequestException, NotFoundException


logger = logging.getLogger(__name__)


class AwsS3DocumentStorageService(DocumentStorageServiceInterface):
    """AWS S3 implementation of document storage service."""
    
    def __init__(self):
        """Initialize S3 client with credentials from settings."""
        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=settings.S3_AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.S3_AWS_SECRET_ACCESS_KEY,
            region_name=settings.S3_AWS_REGION
        )
        self.bucket_name = settings.S3_BUCKET_NAME
        self.cdn_url = settings.S3_CDN_URL
    
    async def upload_file(
        self,
        file: UploadFile,
        file_path: str,
        allowed_extensions: list[str]
    ) -> str | None:
        """
        Upload a file to AWS S3.
        
        Args:
            file: The file to upload
            file_path: The destination path/key in S3
            allowed_extensions: List of allowed file extensions (e.g., ['.jpg', '.png'])
            
        Returns:
            The public CDN URL of the uploaded file, or None if validation fails
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
            
            # Determine content type
            content_type = file.content_type or "application/octet-stream"
            
            # Upload to S3 using asyncio.to_thread for async compatibility
            await asyncio.to_thread(
                self.s3_client.upload_fileobj,
                file_stream,
                self.bucket_name,
                file_path,
                ExtraArgs={"ContentType": content_type}
            )
            
            # Reset file position for potential reuse
            await file.seek(0)
            
            # Return CDN URL or S3 bucket URL
            return self._build_file_url(file_path)
            
        except ClientError as e:
            # Log error in production
            logger.error(f"Error uploading file to S3: {e}")
            raise BadRequestException("file", f"Failed to upload file to S3: {str(e)}")
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
        Upload a file from a stream to AWS S3.
        
        Args:
            stream: The byte stream to upload
            file_path: The destination path/key in S3
            content_type: The MIME type of the file
            
        Returns:
            The public CDN URL of the uploaded file, or None if upload fails
        """
        # Validate stream is not null
        if stream is None:
            raise BadRequestException("stream", "No stream provided")
        
        try:
            # Upload to S3 using asyncio.to_thread for async compatibility
            await asyncio.to_thread(
                self.s3_client.upload_fileobj,
                stream,
                self.bucket_name,
                file_path,
                ExtraArgs={"ContentType": content_type}
            )
            
            # Return CDN URL or S3 bucket URL
            return self._build_file_url(file_path)
            
        except ClientError as e:
            logger.error(f"Error uploading stream to S3: {e}")
            raise BadRequestException("stream", f"Failed to upload stream to S3: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error during stream upload: {e}")
            raise BadRequestException("stream", f"Unexpected error during stream upload: {str(e)}")
    
    async def remove(
        self,
        key: str
    ) -> ResponseMeta:
        """
        Remove a file from AWS S3.
        
        Args:
            key: The file key/path or full CDN URL
            
        Returns:
            ResponseMeta with success or error message
        """
        try:
            # Strip CDN URL from key if present
            if self.cdn_url and key.startswith(self.cdn_url):
                # Remove CDN URL prefix and leading slash
                key = key.replace(self.cdn_url, "").lstrip("/")
            # Strip S3 bucket URL from key if present
            elif key.startswith(f"https://{self.bucket_name}.s3.{settings.S3_AWS_REGION}.amazonaws.com/"):
                key = key.replace(f"https://{self.bucket_name}.s3.{settings.S3_AWS_REGION}.amazonaws.com/", "")
            
            # Validate key is not empty after stripping
            if not key:
                return ResponseMeta(message="Invalid file key")
            
            # Check if object exists before deleting
            try:
                await asyncio.to_thread(
                    self.s3_client.head_object,
                    Bucket=self.bucket_name,
                    Key=key
                )
            except ClientError as e:
                if e.response['Error']['Code'] == '404':
                    return ResponseMeta(message="File not found")
                raise
            
            # Delete object from S3 using asyncio.to_thread for async compatibility
            await asyncio.to_thread(
                self.s3_client.delete_object,
                Bucket=self.bucket_name,
                Key=key
            )
            
            return ResponseMeta(message="File deleted successfully")
            
        except ClientError as e:
            error_message = f"Error deleting file from S3: {str(e)}"
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
        Copy a file from one location to another within AWS S3.
        
        Args:
            source_key: The source file key/path or full CDN URL
            destination_key: The destination file key/path
            
        Returns:
            The public CDN URL of the copied file, or None if copy failed
        """
        try:
            # Strip CDN URL from source_key if present
            if self.cdn_url and source_key.startswith(self.cdn_url):
                source_key = source_key.replace(self.cdn_url, "").lstrip("/")
            # Strip S3 bucket URL from source_key if present
            elif source_key.startswith(f"https://{self.bucket_name}.s3.{settings.S3_AWS_REGION}.amazonaws.com/"):
                source_key = source_key.replace(f"https://{self.bucket_name}.s3.{settings.S3_AWS_REGION}.amazonaws.com/", "")
            
            # Validate keys are not empty
            if not source_key or not destination_key:
                raise BadRequestException("file_key", "Source key and destination key are required")
            
            # Check if source object exists
            try:
                await asyncio.to_thread(
                    self.s3_client.head_object,
                    Bucket=self.bucket_name,
                    Key=source_key
                )
            except ClientError as e:
                if e.response['Error']['Code'] == '404':
                    raise NotFoundException("source_key", f"Source file not found: {source_key}")
                raise
            
            # Copy object in S3 using asyncio.to_thread for async compatibility
            copy_source = {
                'Bucket': self.bucket_name,
                'Key': source_key
            }
            
            await asyncio.to_thread(
                self.s3_client.copy_object,
                CopySource=copy_source,
                Bucket=self.bucket_name,
                Key=destination_key
            )
            
            # Return CDN URL of the copied file
            return self._build_file_url(destination_key)
            
        except ClientError as e:
            logger.error(f"Error copying file in S3: {e}")
            raise BadRequestException("copy", f"Failed to copy file in S3: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error during file copy: {e}")
            raise BadRequestException("copy", f"Unexpected error during file copy: {str(e)}")
    
    async def move(
        self,
        source_key: str,
        destination_key: str
    ) -> str | None:
        """
        Move a file from one location to another within AWS S3.
        This is implemented as copy + delete.
        
        Args:
            source_key: The source file key/path or full CDN URL
            destination_key: The destination file key/path
            
        Returns:
            The public CDN URL of the moved file, or None if move failed
        """
        try:
            # First, copy the file
            copied_url = await self.copy(source_key, destination_key)
            
            # Then, delete the source file
            # We need the stripped key for deletion
            stripped_source_key = source_key
            if self.cdn_url and source_key.startswith(self.cdn_url):
                stripped_source_key = source_key.replace(self.cdn_url, "").lstrip("/")
            elif source_key.startswith(f"https://{self.bucket_name}.s3.{settings.S3_AWS_REGION}.amazonaws.com/"):
                stripped_source_key = source_key.replace(f"https://{self.bucket_name}.s3.{settings.S3_AWS_REGION}.amazonaws.com/", "")
            
            await asyncio.to_thread(
                self.s3_client.delete_object,
                Bucket=self.bucket_name,
                Key=stripped_source_key
            )
            
            return copied_url
            
        except BadRequestException:
            # Re-raise BadRequestException from copy method
            raise
        except NotFoundException:
            # Re-raise NotFoundException from copy method
            raise
        except ClientError as e:
            logger.error(f"Error moving file in S3: {e}")
            raise BadRequestException("move", f"Failed to move file in S3: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error during file move: {e}")
            raise BadRequestException("move", f"Unexpected error during file move: {str(e)}")
    
    def _build_file_url(self, file_path: str) -> str:
        """
        Build the file URL using CDN URL if available, otherwise use S3 bucket URL.
        
        Args:
            file_path: The file path/key in S3
            
        Returns:
            The complete URL to access the file
        """
        if self.cdn_url:
            return f"{self.cdn_url}/{file_path}"
        else:
            return f"https://{self.bucket_name}.s3.{settings.S3_AWS_REGION}.amazonaws.com/{file_path}"
