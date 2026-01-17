from pydantic import BaseModel


class DocumentOperationResponse(BaseModel):
    message: str
    url: str
