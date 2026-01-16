from abc import ABC, abstractmethod
from typing import IO
from fastapi import UploadFile
from app.schema.response.meta import ResponseMeta


class DocumentStorageServiceInterface(ABC):
    """Abstract base class for document storage operations."""
    
    @abstractmethod
    async def upload_file(
        self,
        file: UploadFile,
        file_path: str,
        allowed_extensions: list[str]
    ) -> str | None:
        """
        Upload a file to storage.
        
        Args:
            file: The file to upload
            file_path: The destination path/key in storage
            allowed_extensions: List of allowed file extensions (e.g., ['.jpg', '.png'])
            
        Returns:
            The public URL of the uploaded file, or None if upload failed
        """
        pass
    
    @abstractmethod
    async def upload_stream(
        self,
        stream: IO[bytes],
        file_path: str,
        content_type: str
    ) -> str | None:
        """
        Upload a file from a stream to storage.
        
        Args:
            stream: The byte stream to upload
            file_path: The destination path/key in storage
            content_type: The MIME type of the file
            
        Returns:
            The public URL of the uploaded file, or None if upload failed
        """
        pass
    
    @abstractmethod
    async def remove(
        self,
        key: str
    ) -> ResponseMeta:
        """
        Remove a file from storage.
        
        Args:
            key: The file key/path or full CDN URL
            
        Returns:
            ResponseMeta with success or error message
        """
        pass
