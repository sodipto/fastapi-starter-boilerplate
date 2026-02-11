from pydantic import BaseModel


class DocumentOperationResponse(BaseModel):
    message: str
    url: str | None = None
    key: str | None = None


class DocumentStorageResponse(BaseModel):
    url: str | None = None
    key: str | None = None
