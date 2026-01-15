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
