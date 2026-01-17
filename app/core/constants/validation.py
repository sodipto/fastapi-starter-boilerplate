import re

# Email validation regex pattern
EMAIL_REGEX = re.compile(
    r"\A(?:[a-zA-Z0-9!#$%&'*+/=?^_`{|}~-]+"
    r"(?:\.[a-zA-Z0-9!#$%&'*+/=?^_`{|}~-]+)*@"
    r"(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]*[a-zA-Z0-9])?\.)+"
    r"[a-zA-Z0-9](?:[a-zA-Z0-9-]*[a-zA-Z0-9])?)\Z"
)

# Alphanumeric validation regex pattern
ALPHANUMERIC_REGEX = re.compile(r'^[a-zA-Z0-9]+$')

# File extension constants
ALLOWED_IMAGE_EXTENSIONS = [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".svg"]
ALLOWED_VIDEO_EXTENSIONS = [".mp4", ".avi", ".mov", ".wmv", ".flv", ".mkv", ".webm"]
ALLOWED_EXCEL_EXTENSIONS = [".xls", ".xlsx", ".xlsm"]
ALLOWED_DOC_EXTENSIONS = [".doc", ".docx"]
ALLOWED_CSV_EXTENSIONS = [".csv"]
ALLOWED_PDF_EXTENSIONS = [".pdf"]
