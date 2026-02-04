import uuid
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi import Request
from app.schema.response.error import ErrorBody, ErrorResponse

async def custom_validation_exception_handler(request: Request, exc: RequestValidationError):
    messages = {}
    for err in exc.errors():
        loc_parts = err.get("loc", [])
        loc = ".".join(str(l) for l in loc_parts)
        if not loc:
            # fallback to error type (e.g. passwords_mismatch). If type contains dots, take last segment.
            err_type = err.get("type", "error")
            loc = str(err_type).split(".")[-1]
        messages[loc] = err.get("msg", "")
    error_body = ErrorBody(
        logId=str(uuid.uuid4()),
        statusCode=422,
        type="BadRequestException",
        messages=messages
    )
    return JSONResponse(
        status_code=400,
        content=ErrorResponse(error=error_body).model_dump()
    )