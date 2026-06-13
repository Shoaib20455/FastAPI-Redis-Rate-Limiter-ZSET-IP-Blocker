# models.py
from pydantic import BaseModel, Field
from typing import Optional

class RateLimitErrorResponse(BaseModel):
    """Response when rate limit is exceeded (HTTP 429)"""
    error: str
    message: str
    limit: int
    retry_after_seconds: int

class IPBlockedResponse(BaseModel):
    """Response when IP is already blocked (HTTP 403)"""
    error: str
    message: str
    retry_after_seconds: int

class IPStatusResponse(BaseModel):
    """Response for admin check-ip endpoint"""
    ip: str
    is_blocked: bool
    block_ttl_seconds: int
    requests_in_window: int
    limit: int

class UnblockResponse(BaseModel):
    """Response for admin unblock endpoint"""
    message: str