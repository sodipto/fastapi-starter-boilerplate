import uuid
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi import Request
from fastapi import status
from app.schema.response.error_schema import ErrorBody, ErrorResponse

def custom_validation_exception_middleware(request: Request, exc: RequestValidationError):
    print(request.method)
    messages = {}
    for err in exc.errors():
        loc_parts = err.get("loc", [])
        if loc_parts and loc_parts[0] == "body":
            loc_parts = loc_parts[1:]  # remove 'body' prefix
        loc = ".".join(str(l) for l in loc_parts)
        messages[loc] = err.get("msg", "")  # use only the message, not the error type

    error_body = ErrorBody(
        logId=str(uuid.uuid4()),
        statusCode=status.HTTP_400_BAD_REQUEST,
        type="BadRequestException",
        messages=messages
    )
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=ErrorResponse(error=error_body).model_dump()
    )

