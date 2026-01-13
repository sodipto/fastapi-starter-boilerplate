PAGE = 1
PAGE_SIZE = 20

def calculate_skip(page: int, page_size: int) -> int:
    """Calculate skip value from page number (1-based)."""
    return (page - 1) * page_size