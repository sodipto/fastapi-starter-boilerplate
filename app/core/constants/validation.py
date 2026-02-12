import re
from pydantic_core import PydanticCustomError

from app.core.config import settings
from app.utils.exception_utils import BadRequestException


# Email validation regex pattern
EMAIL_REGEX = re.compile(
    r"\A(?:[a-zA-Z0-9!#$%&'*+/=?^_`{|}~-]+"
    r"(?:\.[a-zA-Z0-9!#$%&'*+/=?^_`{|}~-]+)*@"
    r"(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]*[a-zA-Z0-9])?\.)+"
    r"[a-zA-Z0-9](?:[a-zA-Z0-9-]*[a-zA-Z0-9])?)\Z"
)


# Alphanumeric validation regex pattern (allow spaces)
# Accept letters, numbers and spaces. Trim/other validation should
# be performed by callers if needed (e.g., disallow leading/trailing spaces).
ALPHANUMERIC_REGEX = re.compile(r'^[a-zA-Z0-9 ]+$')


# Secure password regex: at least PASSWORD_MIN_LENGTH characters, one uppercase, one lowercase, one digit, one special char
SECURE_PASSWORD_REGEX = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{' + str(settings.PASSWORD_MIN_LENGTH) + r',}$')


def is_secure_password(value: str) -> bool:
    return bool(SECURE_PASSWORD_REGEX.match(value))


def validate_password_with_policy(value: str, *, min_length: int, max_length: int | None = None, field_name: str = "password") -> str:
    # Validate min_length parameter
    if not isinstance(min_length, int) or min_length <= 0:
        raise BadRequestException("password_length","min_length must be a positive integer")

    # If secure password enforcement enabled, apply regex
    if settings.SECURE_PASSWORD:
        if not is_secure_password(value):
            raise PydanticCustomError(
                "password_not_secure",
                f"{field_name} must be at least {min_length} characters long and include uppercase, lowercase, digit and special character!"
            )
        return value

    # Enforce provided min/max length
    if len(value) < min_length:
        raise PydanticCustomError(
            "password_too_short",
            f"{field_name} must be at least {min_length} characters"
        )
    if max_length is not None and len(value) > max_length:
        raise PydanticCustomError(
            "password_too_long",
            f"{field_name} must be at most {max_length} characters"
        )
    return value
