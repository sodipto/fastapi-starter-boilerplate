import asyncio
import os
from typing import IO
from io import BytesIO
import boto3
from botocore.exceptions import ClientError
from fastapi import UploadFile
from app.core.config import settings
from app.services.interfaces.document_storage_service_interface import DocumentStorageServiceInterface
from app.schema.response.meta import ResponseMeta


class AwsS3DocumentStorageService(DocumentStorageServiceInterface):
    """AWS S3 implementation of document storage service."""
    
    def __init__(self):
        """Initialize S3 client with credentials from settings."""
        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
        self.bucket_name = settings.BUCKET_NAME
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
            return None
        
        # Validate file has a filename
        if not file.filename:
            return None
        
        # Get file extension
        _, file_extension = os.path.splitext(file.filename)
        
        # Validate file has an extension
        if not file_extension:
            return None
        
        # Normalize extension to lowercase
        file_extension = file_extension.lower()
        
        # Normalize allowed extensions to lowercase
        normalized_allowed_extensions = [ext.lower() for ext in allowed_extensions]
        
        # Validate extension is in allowed list
        if file_extension not in normalized_allowed_extensions:
            return None
        
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
            print(f"Error uploading file to S3: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error during file upload: {e}")
            return None
    
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
            return None
        
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
            print(f"Error uploading stream to S3: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error during stream upload: {e}")
            return None
    
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
            elif key.startswith(f"https://{self.bucket_name}.s3.{settings.AWS_REGION}.amazonaws.com/"):
                key = key.replace(f"https://{self.bucket_name}.s3.{settings.AWS_REGION}.amazonaws.com/", "")
            
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
            print(error_message)
            return ResponseMeta(message=error_message)
        except Exception as e:
            error_message = f"Unexpected error during file deletion: {str(e)}"
            print(error_message)
            return ResponseMeta(message=error_message)
    
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
            return f"https://{self.bucket_name}.s3.{settings.AWS_REGION}.amazonaws.com/{file_path}"
