"""
Request Models Module
Single responsibility: Define request data structures.

Models:
- ProductSearchRequest: Product search with crawler protection
"""

from pydantic import BaseModel, Field
from typing import Optional


class ProductSearchRequest(BaseModel):
    """Schema for searching products by category."""

    category: str = Field(
        ...,
        description="Product category (electronics, clothing, books, home)",
        example="electronics"
    )
    page: int = Field(
        default=1,
        ge=1,
        description="Page number (1-indexed)"
    )
    limit: int = Field(
        default=20,
        ge=1,
        le=50,
        description="Results per page (max 50 to prevent crawler abuse)"
    )
    sort_by: Optional[str] = Field(
        default="relevance",
        description="Sort order (relevance, price_asc, price_desc)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "category": "electronics",
                "page": 1,
                "limit": 20
            }
        }
