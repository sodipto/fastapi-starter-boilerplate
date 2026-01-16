import enum


class EmailStatus(str, enum.Enum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
