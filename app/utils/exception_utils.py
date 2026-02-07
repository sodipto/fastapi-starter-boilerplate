from fastapi import status

class BadRequestException(Exception):
    def __init__(self, key: str, message: str):
        self.type = "BadRequestException"
        self.status_code = status.HTTP_400_BAD_REQUEST
        self.messages = {
            key: message,
        }


class NotFoundException(Exception):
    def __init__(self, key: str, message: str):
        self.type = "NotFoundException"
        self.status_code = status.HTTP_404_NOT_FOUND
        self.messages = {
            key: message,
        }

class UnauthorizedException(Exception):
    def __init__(self, message: str):
        self.type = "UnauthorizedException"
        self.status_code = status.HTTP_401_UNAUTHORIZED
        self.messages = {
            "Unauthorized": message,
        }


class ForbiddenException(Exception):
    def __init__(self, key: str, message: str):
        self.type = "ForbiddenException"
        self.status_code = status.HTTP_403_FORBIDDEN
        self.messages = {
            key: message,
        }


class ConflictException(Exception):
    def __init__(self, key: str, message: str):
        self.type = "ConflictException"
        self.status_code = status.HTTP_409_CONFLICT
        self.messages = {
            key: message,
        }


class TooManyRequestsException(Exception):
    def __init__(self, retry_after: int = 1):
        self.type = "TooManyRequestsException"
        self.status_code = status.HTTP_429_TOO_MANY_REQUESTS
        self.retry_after = retry_after
        self.messages = {
            "RateLimit": f"Too many requests. Please retry after {retry_after} seconds.",
        }