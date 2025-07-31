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