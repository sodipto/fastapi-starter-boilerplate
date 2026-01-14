from typing import Generic, TypeVar, List
from pydantic import BaseModel, Field

T = TypeVar("T")


class PagedMeta(BaseModel):
    """Metadata for paginated responses."""
    
    total_count: int = Field(..., description="Total number of items")
    page_size: int = Field(..., description="Number of items per page")
    current_page: int = Field(..., description="Current page number (1-based)")
    total_pages: int = Field(..., description="Total number of pages")
    has_previous_page: bool = Field(..., description="Whether there is a previous page")
    has_next_page: bool = Field(..., description="Whether there is a next page")


class PagedData(BaseModel, Generic[T]):
    """Generic paged response model similar to .NET PagedData<T>."""
    
    data: List[T] = Field(..., description="List of items for the current page")
    meta: PagedMeta = Field(..., description="Pagination metadata")
    
    @staticmethod
    def create(
        data: List[T],
        total_count: int,
        page: int,
        page_size: int
    ) -> "PagedData[T]":
        """
        Create a PagedData instance with calculated metadata.
        
        Args:
            data: List of items for the current page
            total_count: Total number of items across all pages
            page: Current page number (1-based)
            page_size: Number of items per page
            
        Returns:
            PagedData instance with populated metadata
        """
        # Calculate total pages correctly, ensuring 0 pages when total_count is 0
        total_pages = (total_count + page_size - 1) // page_size if total_count > 0 and page_size > 0 else 0
        
        meta = PagedMeta(
            total_count=total_count,
            page_size=page_size,
            current_page=page,
            total_pages=total_pages,
            has_previous_page=page > 1,
            has_next_page=page < total_pages
        )
        
        return PagedData(data=data, meta=meta)


def create_paged_response(
    items: List[T],
    total_count: int,
    page: int,
    page_size: int
) -> PagedData[T]:
    """
    Reusable pagination helper that converts items and pagination info into PagedData[T].
    
    Args:
        items: List of items for the current page
        total_count: Total number of items across all pages
        page: Current page number (1-based)
        page_size: Number of items per page
        
    Returns:
        PagedData instance with populated metadata
        
    """
    return PagedData.create(items, total_count, page, page_size)
