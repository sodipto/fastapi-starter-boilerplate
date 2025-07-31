from pydantic import BaseModel
from typing import Dict


class ErrorBody(BaseModel):
    logId: str
    statusCode: int
    type: str
    messages: Dict[str, str]


class ErrorResponse(BaseModel):
    error: ErrorBody