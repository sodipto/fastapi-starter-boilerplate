# Document Storage

This boilerplate supports multiple object storage providers through a unified interface, allowing seamless switching between cloud and on-premise deployments.

## Supported Providers

| Provider | Use Case | Configuration Prefix |
|----------|----------|---------------------|
| **AWS S3** | Cloud deployments | `S3_*` |
| **MinIO** | On-premise / self-hosted | `MINIO_*` |

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Endpoints                           │
│              (app/api/endpoints/v1/document.py)         │
└─────────────────────┬───────────────────────────────────┘
                      │ Depends(Provide[Container.document_storage_service])
                      ▼
┌─────────────────────────────────────────────────────────┐
│           DocumentStorageServiceInterface               │
│        (app/services/interfaces/...)                    │
└─────────────────────┬───────────────────────────────────┘
                      │
        ┌─────────────┴─────────────┐
        ▼                           ▼
┌───────────────────┐     ┌───────────────────┐
│ AwsS3Document     │     │ MinioDocument     │
│ StorageService    │     │ StorageService    │
└───────────────────┘     └───────────────────┘
        │                           │
        ▼                           ▼
   AWS S3 API                 MinIO API
   (boto3)                    (minio-py)
```

## Configuration

### Selecting a Provider

Set the `STORAGE_PROVIDER` environment variable to switch between providers:

```dotenv
# Use AWS S3 (default)
STORAGE_PROVIDER=aws

# Use MinIO (on-premise)
STORAGE_PROVIDER=minio
```

### Presigned URL Configuration

When a CDN URL is not configured, the storage service automatically generates **presigned URLs** for secure, time-limited file access. This is useful for private buckets where direct public access is not desired.

```dotenv
# Expiration time for presigned URLs (in minutes)
PRESIGNED_URL_EXPIRE_MINUTES=10
```

**URL Generation Behavior:**

| CDN URL | Behavior |
|---------|----------|
| Configured (`S3_CDN_URL` or `MINIO_CDN_URL`) | Returns CDN URL (e.g., `https://cdn.example.com/path/file.jpg`) |
| Empty or not set | Returns presigned URL with expiration (e.g., `https://bucket.s3.region.amazonaws.com/path/file.jpg?X-Amz-...&Expires=...`) |

**Security considerations:**
- Presigned URLs are temporary and expire after `PRESIGNED_URL_EXPIRE_MINUTES`
- Each URL contains a signature that grants read access to the specific object
- URLs cannot be reused after expiration
- Recommended for private file access patterns

### AWS S3 Configuration

Required when `STORAGE_PROVIDER=aws`:

```dotenv
S3_AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
S3_AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
S3_AWS_REGION=us-east-1
S3_BUCKET_NAME=my-app-uploads
S3_CDN_URL=https://d1234567890.cloudfront.net  # Optional: CloudFront CDN URL (empty = use presigned URLs)
```

### MinIO Configuration

Required when `STORAGE_PROVIDER=minio`:

```dotenv
MINIO_ENDPOINT=minio.example.com:9000    # Or localhost:9000 for local development
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET_NAME=uploads
MINIO_USE_SSL=false                       # Set to true for HTTPS
MINIO_CDN_URL=                            # Optional: CDN URL (empty = use presigned URLs)
```

## Local Development with MinIO

### Option 1: Docker Compose (Recommended)

Add MinIO to your `docker-compose.yml`:

```yaml
services:
  minio:
    image: minio/minio:latest
    container_name: minio
    ports:
      - "9000:9000"   # API
      - "9001:9001"   # Console
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin
    command: server /data --console-address ":9001"
    volumes:
      - minio_data:/data
    healthcheck:
      test: ["CMD", "mc", "ready", "local"]
      interval: 5s
      timeout: 5s
      retries: 5

volumes:
  minio_data:
```

Then start with:

```bash
docker-compose up -d minio
```

### Option 2: Standalone Docker

```bash
docker run -d \
  --name minio \
  -p 9000:9000 \
  -p 9001:9001 \
  -e MINIO_ROOT_USER=minioadmin \
  -e MINIO_ROOT_PASSWORD=minioadmin \
  minio/minio server /data --console-address ":9001"
```

### Accessing MinIO Console

Open http://localhost:9001 in your browser and login with:
- Username: `minioadmin`
- Password: `minioadmin`

## Interface Methods

All storage providers implement these methods:

| Method | Description |
|--------|-------------|
| `upload_file(file, file_path, allowed_extensions)` | Upload file with extension validation |
| `upload_stream(stream, file_path, content_type)` | Upload from byte stream |
| `remove(key)` | Delete file by key or URL |
| `copy(source_key, destination_key)` | Copy file within storage |
| `move(source_key, destination_key)` | Move file (copy + delete) |

## Usage Example

```python
from dependency_injector.wiring import inject, Provide
from fastapi import Depends, UploadFile, File
from app.core.container import Container
from app.services.interfaces.document_storage_service_interface import DocumentStorageServiceInterface
from app.core.constants.file_extensions import ALLOWED_IMAGE_EXTENSIONS

@router.post("/upload")
@inject
async def upload_document(
    file: UploadFile = File(...),
    storage_service: DocumentStorageServiceInterface = Depends(
        Provide[Container.document_storage_service]
    )
):
    url = await storage_service.upload_file(
        file=file,
        file_path=f"documents/{file.filename}",
        allowed_extensions=ALLOWED_IMAGE_EXTENSIONS
    )
    return {"url": url}
```

## Production Considerations

### AWS S3

1. **IAM Permissions**: Create a dedicated IAM user with minimal permissions:
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Allow",
         "Action": [
           "s3:PutObject",
           "s3:GetObject",
           "s3:DeleteObject",
           "s3:CopyObject"
         ],
         "Resource": "arn:aws:s3:::your-bucket-name/*"
       }
     ]
   }
   ```

2. **CloudFront CDN**: Configure CloudFront for better performance and cost optimization.

3. **Bucket Policies**: Enable versioning and lifecycle rules for production buckets.

### MinIO

1. **TLS/SSL**: Always enable `MINIO_USE_SSL=true` in production.

2. **Authentication**: Use strong, unique access keys (not the default `minioadmin`).

3. **High Availability**: Deploy MinIO in distributed mode for production:
   ```bash
   minio server http://minio{1...4}/data{1...2}
   ```

4. **Backup**: Configure regular backups using MinIO Client (`mc mirror`).

5. **Monitoring**: Enable Prometheus metrics endpoint for observability.

## Adding New Storage Providers

To add a new provider (e.g., Azure Blob Storage):

1. Create `app/services/azure_blob_storage_service.py` implementing `DocumentStorageServiceInterface`

2. Add provider type to `StorageProviderType` enum in `storage_service_factory.py`:
   ```python
   class StorageProviderType(str, Enum):
       AWS = "aws"
       MINIO = "minio"
       AZURE = "azure"  # New provider
   ```

3. Add factory branch in `StorageServiceFactory.create()`:
   ```python
   elif provider == StorageProviderType.AZURE.value:
       from app.services.azure_blob_storage_service import AzureBlobStorageService
       return AzureBlobStorageService()
   ```

4. Add configuration settings with `AZURE_*` prefix to `config.py`

5. Update `.env.development` and `.env.production` with new settings
