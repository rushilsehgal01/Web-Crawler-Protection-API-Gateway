"""
Response Models Module
Single responsibility: Define response data structures.

Models:
- APIResponse: Standard success response
- RateLimitResponse: Rate limit error response
"""

from pydantic import BaseModel
from typing import Optional, Dict, Any


class APIResponse(BaseModel):
    """Standard API response for successful requests."""

    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class RateLimitResponse(BaseModel):
    """Response when a request is rate limited."""

    success: bool = False
    message: str = "Rate limit exceeded"
    error: str = "Too many requests"
    retry_after_seconds: int = 1
