import uuid
import json
import traceback

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse
from app.schema.response.error import ErrorBody, ErrorResponse
from app.utils.exception_utils import BadRequestException, ConflictException, ForbiddenException, NotFoundException, UnauthorizedException
from app.core.logger import get_logger
from app.core.jwt_security import decode_jwt
try:
    from seqlog.structured_logging import StructuredLogger
except ImportError:
    StructuredLogger = None

logger = get_logger(__name__)


class CustomExceptionMiddleware(BaseHTTPMiddleware):
    
    def _extract_user_id(self, request: Request) -> str:
        """Extract user_id from JWT token if available."""
        try:
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]
                payload = decode_jwt(token)
                if payload:
                    user_id = payload.get("user_id")
                    return str(user_id) if user_id else "Anonymous"
        except Exception:
            pass
        return "Anonymous"
    
    def _log_error(self, log_id: str, user_id: str, error_type: str, status_code: int, 
                   error_response: ErrorResponse, request: Request, stack_trace: str = None):
        """Log error with template and structured properties."""
        # Build formatted message for display
        error_info_str = json.dumps(error_response.model_dump(), indent=2)
        message_parts = [
            f"UserId:{user_id}",
            f"LogId:{log_id}",
            f"Type:{error_type}",
            f"StatusCode:{status_code}",
            f"Path:{request.method} {request.url.path}",
            f"ErrorInformation:{error_info_str}"
        ]
        
        formatted_message = "\n".join(message_parts)

        # Structured properties for Seq (assuming support_extra_properties=True)
        props = {
            "UserId": user_id,
            "LogId": log_id,
            "Type": error_type,
            "StatusCode": status_code,
            "ErrorInfo": error_response.model_dump(),
            "HttpMethod": request.method,
            "Path": str(request.url.path),
            "ClientHost": request.client.host if request.client else None
        }
        
        if stack_trace:
            props["StackTrace"] = stack_trace
        
        if StructuredLogger and isinstance(logger, StructuredLogger):
            logger.error(formatted_message, **props)
        else:
            logger.error(formatted_message, extra=props)
    
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
            
        except (BadRequestException, NotFoundException, UnauthorizedException, ForbiddenException, ConflictException) as e:
            log_id = str(uuid.uuid4())
            user_id = self._extract_user_id(request)
            
            error_response = ErrorResponse(
                error=ErrorBody(
                    logId=log_id,
                    statusCode=e.status_code,
                    type=e.type,
                    messages=e.messages
                )
            )
            
            self._log_error(log_id, user_id, e.type, e.status_code, error_response, request)
            
            return JSONResponse(
                status_code=e.status_code,
                content=error_response.model_dump()
            )
            
        except Exception as e:
            log_id = str(uuid.uuid4())
            user_id = self._extract_user_id(request)
            stack_trace = traceback.format_exc()
            
            error_response = ErrorResponse(
                error=ErrorBody(
                    logId=log_id,
                    statusCode=500,
                    type="InternalServerError",
                    messages={"message": str(e)}
                )
            )
            
            self._log_error(log_id, user_id, "InternalServerError", 500, error_response, request, stack_trace)
            
            return JSONResponse(
                status_code=500,
                content=error_response.model_dump()
            )