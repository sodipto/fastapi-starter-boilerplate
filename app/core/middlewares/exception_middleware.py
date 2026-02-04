import uuid

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse
from app.schema.response.error import ErrorBody, ErrorResponse
from app.utils.exception_utils import BadRequestException, ConflictException, ForbiddenException, NotFoundException, UnauthorizedException
from app.core.logger import get_logger

logger = get_logger(__name__)

class CustomExceptionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except (BadRequestException, NotFoundException, UnauthorizedException,ForbiddenException, ConflictException) as e:
            log_id = str(uuid.uuid4())
            error_response = ErrorResponse(
                error=ErrorBody(
                    logId=log_id,
                    statusCode=e.status_code,
                    type=e.type,
                    messages=e.messages
                )
            )
            
            # Log the custom exception
            logger.error(
                f"[LogID: {log_id}] {e.type} - Status: {e.status_code} - "
                f"Path: {request.method} {request.url.path} - Messages: {e.messages}"
            )
            
            return JSONResponse(
                status_code=e.status_code,
                content=error_response.model_dump()
            )
        except Exception as e:
            log_id = str(uuid.uuid4())
            error_response = ErrorResponse(
                error=ErrorBody(
                    logId=log_id,
                    statusCode=500,
                    type="InternalServerError",
                    messages={"message": str(e)}
                )
            )
            
            # Log the unhandled exception with full traceback
            logger.error(
                f"[LogID: {log_id}] Unhandled exception - Path: {request.method} {request.url.path}",
                exc_info=True
            )
            
            return JSONResponse(
                status_code=500,
                content=error_response.model_dump()
            )