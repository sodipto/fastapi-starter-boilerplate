import uuid
import json
import traceback

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse
from app.schema.response.error import ErrorBody, ErrorResponse
from app.utils.exception_utils import BadRequestException, ConflictException, ForbiddenException, NotFoundException, UnauthorizedException, TooManyRequestsException
from app.core.logger import get_logger
from app.core.identity import extract_user_id_from_request
try:
    from seqlog.structured_logging import StructuredLogger
except ImportError:
    StructuredLogger = None

logger = get_logger(__name__)


class CustomExceptionMiddleware(BaseHTTPMiddleware):
    
    def _log_error(self, log_id: str, user_id: str, error_type: str, status_code: int, 
                   error_response: ErrorResponse, request: Request, stack_trace: str = None):
        """Log error with template and structured properties."""
        # Build formatted message for display
        messages_json = json.dumps(error_response.error.messages, indent=2)
        message_parts = [
            f"Type:{error_type}({status_code})",
            f"Path:{request.method} {request.url.path}",
            f"Error:{messages_json}"
        ]
        
        formatted_message = "\n".join(message_parts)

        # Structured properties for Seq (assuming support_extra_properties=True)
        props = {
            "UserId": user_id,
            "LogId": log_id,
            "Type": error_type,
            "StatusCode": status_code,
            "Error": messages_json,
            "HttpMethod": request.method,
            "Path": str(request.url.path),
            "Host": request.client.host if request.client else None
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
            user_id = extract_user_id_from_request(request)
            
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
        
        except TooManyRequestsException as e:
            log_id = str(uuid.uuid4())
            user_id = extract_user_id_from_request(request)
            
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
                content=error_response.model_dump(),
                headers={"Retry-After": str(e.retry_after)}
            )
            
        except Exception as e:
            log_id = str(uuid.uuid4())
            user_id = extract_user_id_from_request(request)
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