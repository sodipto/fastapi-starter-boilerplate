"""
Storage Service Factory

Factory pattern implementation for selecting the appropriate document storage provider
based on configuration. Supports AWS S3 and MinIO (S3-compatible) for on-premise deployments.

Usage:
    The factory reads STORAGE_PROVIDER from settings and returns the appropriate
    implementation of DocumentStorageServiceInterface.
    
    Supported providers:
        - "aws": AWS S3 storage (default)
        - "minio": MinIO S3-compatible storage for on-premise
"""
import logging
from enum import Enum

from app.core.config import settings
from app.services.interfaces.document_storage_service_interface import DocumentStorageServiceInterface


logger = logging.getLogger(__name__)


class StorageProviderType(str, Enum):
    """Supported storage provider types."""
    AWS = "aws"
    MINIO = "minio"


class StorageServiceFactory:
    """
    Factory for creating document storage service instances.
    
    Uses the STORAGE_PROVIDER setting to determine which implementation to instantiate.
    This allows seamless switching between cloud (AWS S3) and on-premise (MinIO) storage
    without changing application code.
    """
    
    @staticmethod
    def create() -> DocumentStorageServiceInterface:
        """
        Create and return the appropriate document storage service based on configuration.
        
        Returns:
            DocumentStorageServiceInterface: The configured storage service instance
            
        Raises:
            ValueError: If STORAGE_PROVIDER is set to an unsupported value
        """
        provider = settings.STORAGE_PROVIDER.lower()
        
        logger.info(f"Initializing document storage service with provider: {provider}")
        
        if provider == StorageProviderType.AWS.value:
            from app.services.AWS_s3_document_storage_service import AwsS3DocumentStorageService
            return AwsS3DocumentStorageService()
        
        elif provider == StorageProviderType.MINIO.value:
            from app.services.minio_document_storage_service import MinioDocumentStorageService
            return MinioDocumentStorageService()
        
        else:
            supported = ", ".join([p.value for p in StorageProviderType])
            raise ValueError(
                f"Unsupported storage provider: '{provider}'. "
                f"Supported providers: {supported}"
            )
