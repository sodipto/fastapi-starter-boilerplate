import uuid
import json
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi import Request
from fastapi import status
from app.schema.response.error import ErrorBody, ErrorResponse
from app.core.logger import get_logger
from app.core.identity import extract_user_id_from_request
try:
    from seqlog.structured_logging import StructuredLogger
except ImportError:
    StructuredLogger = None

logger = get_logger(__name__)

def _log_validation_errors(log_id: str, messages: dict, request: Request, user_id: str):
    error_info = json.dumps({"messages": messages}, indent=2)
    message_parts = [
            f"Type:BadRequestException ({status.HTTP_400_BAD_REQUEST})",
            f"Path:{request.method} {request.url.path}",
            f"Error:{error_info}"
    ]
    formatted_message = "\n".join(message_parts)

    props = {
        "UserId": user_id,
        "LogId": log_id,
        "Type": "BadRequestException",
        "StatusCode": status.HTTP_400_BAD_REQUEST,
        "Error": messages,
        "Path": str(request.url.path),
        "HttpMethod": request.method,
        "ClientHost": request.client.host if request.client else None
    }
    
    if StructuredLogger and isinstance(logger, StructuredLogger):
        logger.error(formatted_message, **props)
    else:
        logger.error(formatted_message, extra=props)

def custom_validation_exception_middleware(request: Request, exc: RequestValidationError):
    messages = {}
    for err in exc.errors():
        loc_parts = err.get("loc", [])
        if loc_parts and loc_parts[0] == "body":
            loc_parts = loc_parts[1:]  # remove 'body' prefix
        loc = ".".join(str(l) for l in loc_parts)
        if not loc:
            err_type = err.get("type", "error")
            loc = str(err_type).split(".")[-1]
        messages[loc] = err.get("msg", "")  # use only the message, not the error type

    error_body = ErrorBody(
        logId=str(uuid.uuid4()),
        statusCode=status.HTTP_400_BAD_REQUEST,
        type="BadRequestException",
        messages=messages
    )
    user_id = extract_user_id_from_request(request)
    _log_validation_errors(error_body.logId, messages, request, user_id)
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=ErrorResponse(error=error_body).model_dump()
    )

