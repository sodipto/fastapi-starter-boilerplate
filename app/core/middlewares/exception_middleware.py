import uuid

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse
from app.schema.response.error import ErrorBody, ErrorResponse
from app.utils.exception_utils import BadRequestException, ConflictException, ForbiddenException, NotFoundException, UnauthorizedException

class CustomExceptionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except (BadRequestException, NotFoundException, UnauthorizedException,ForbiddenException, ConflictException) as e:
            error_response = ErrorResponse(
                error=ErrorBody(
                    logId=str(uuid.uuid4()),
                    statusCode=e.status_code,
                    type=e.type,
                    messages=e.messages
                )
            )
            return JSONResponse(
                status_code=e.status_code,
                content=error_response.model_dump()
            )
        except Exception as e:
            error_response = ErrorResponse(
                error=ErrorBody(
                    logId=str(uuid.uuid4()),
                    statusCode=500,
                    type="InternalServerError",
                    messages={"message": str(e)}
                )
            )
            return JSONResponse(
                status_code=500,
                content=error_response.model_dump()
            )