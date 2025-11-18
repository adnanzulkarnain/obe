"""
Base Pydantic Schemas

Common schemas used across all API endpoints.
Following Clean Code: DRY, Reusability, Type safety.
"""

from typing import TypeVar, Generic, Optional, Any, List
from pydantic import BaseModel, Field
from datetime import datetime


class BaseResponse(BaseModel):
    """
    Base response schema for all API responses.

    Provides consistent response structure across all endpoints.
    """

    success: bool = Field(description="Indicates if request was successful")
    message: Optional[str] = Field(None, description="Response message")

    class Config:
        """Pydantic configuration."""
        from_attributes = True  # Allows creation from ORM objects


T = TypeVar('T')


class SuccessResponse(BaseResponse, Generic[T]):
    """
    Success response with data.

    Generic type parameter T allows type-safe data field.
    """

    success: bool = Field(default=True, description="Always True for success")
    data: T = Field(description="Response data")


class ErrorResponse(BaseResponse):
    """
    Error response schema.

    Used for all error responses with consistent structure.
    """

    success: bool = Field(default=False, description="Always False for errors")
    error_code: str = Field(description="Error code for client handling")
    details: Optional[Any] = Field(None, description="Additional error details")


class PaginationParams(BaseModel):
    """
    Pagination parameters for list endpoints.

    Provides consistent pagination across all list endpoints.
    """

    skip: int = Field(default=0, ge=0, description="Number of records to skip")
    limit: int = Field(default=100, ge=1, le=1000, description="Maximum records to return")


class PaginatedResponse(BaseModel, Generic[T]):
    """
    Paginated response schema.

    Used for list endpoints with pagination support.
    """

    success: bool = Field(default=True, description="Request success status")
    data: List[T] = Field(description="List of items")
    pagination: 'PaginationMeta' = Field(description="Pagination metadata")


class PaginationMeta(BaseModel):
    """
    Pagination metadata.

    Provides information about the current page and total records.
    """

    total: int = Field(description="Total number of records")
    skip: int = Field(description="Number of records skipped")
    limit: int = Field(description="Maximum records returned")
    has_more: bool = Field(description="Whether more records are available")

    @staticmethod
    def create(total: int, skip: int, limit: int) -> 'PaginationMeta':
        """
        Create pagination metadata.

        Args:
            total: Total number of records
            skip: Number of records skipped
            limit: Maximum records returned

        Returns:
            PaginationMeta: Pagination metadata instance
        """
        has_more = (skip + limit) < total
        return PaginationMeta(
            total=total,
            skip=skip,
            limit=limit,
            has_more=has_more
        )


class TimestampMixin(BaseModel):
    """
    Mixin for entities with timestamps.

    Provides created_at and updated_at fields.
    """

    created_at: datetime = Field(description="Creation timestamp")
    updated_at: datetime = Field(description="Last update timestamp")

    class Config:
        """Pydantic configuration."""
        from_attributes = True


class IDResponse(BaseModel):
    """
    Simple response with just an ID.

    Used for operations that only return an ID (e.g., after creation).
    """

    id: int = Field(description="Entity ID")
    message: Optional[str] = Field(None, description="Optional message")


class StatusResponse(BaseModel):
    """
    Simple status response.

    Used for operations that don't return data (e.g., delete, activate).
    """

    success: bool = Field(description="Operation success status")
    message: str = Field(description="Status message")
