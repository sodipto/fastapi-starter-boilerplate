from pydantic import BaseModel


class ResponseMeta(BaseModel):
    message: str
