from abc import ABC, abstractmethod
from typing import IO
from fastapi import UploadFile
from app.schema.response.meta import ResponseMeta
from app.schema.response.document import DocumentStorageResponse


class DocumentStorageServiceInterface(ABC):
    """Abstract base class for document storage operations."""
    
    @abstractmethod
    async def upload_file(
        self,
        file: UploadFile,
        file_path: str,
        allowed_extensions: list[str]
    ) -> DocumentStorageResponse | None:
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
    ) -> DocumentStorageResponse | None:
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
    
    @abstractmethod
    async def copy(
        self,
        source_key: str,
        destination_key: str
    ) -> DocumentStorageResponse | None:
        """
        Copy a file from one location to another within storage.
        
        Args:
            source_key: The source file key/path or full CDN URL
            destination_key: The destination file key/path
            
        Returns:
            The public URL of the copied file, or None if copy failed
        """
        pass
    
    @abstractmethod
    async def move(
        self,
        source_key: str,
        destination_key: str
    ) -> DocumentStorageResponse | None:
        """
        Move a file from one location to another within storage.
        
        Args:
            source_key: The source file key/path or full CDN URL
            destination_key: The destination file key/path
            
        Returns:
            The public URL of the moved file, or None if move failed
        """
        pass
