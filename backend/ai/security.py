"""
Security and rate limiting for AI endpoints.

This module provides rate limiting, input validation, and security measures
for the AI API endpoints.
"""

import time
import hashlib
import logging
from typing import Dict, Optional
from collections import defaultdict, deque
from functools import wraps
from fastapi import HTTPException, Request
import re

logger = logging.getLogger(__name__)

class RateLimiter:
    """Rate limiter implementation using sliding window."""
    
    def __init__(self, max_requests: int = 60, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = defaultdict(deque)
    
    def is_allowed(self, client_id: str) -> bool:
        """
        Check if client is allowed to make a request.
        
        Args:
            client_id: Unique identifier for the client
            
        Returns:
            True if request is allowed, False otherwise
        """
        now = time.time()
        client_requests = self.requests[client_id]
        
        # Remove old requests outside the window
        while client_requests and client_requests[0] <= now - self.window_seconds:
            client_requests.popleft()
        
        # Check if under limit
        if len(client_requests) >= self.max_requests:
            return False
        
        # Add current request
        client_requests.append(now)
        return True
    
    def get_reset_time(self, client_id: str) -> float:
        """Get time when rate limit resets for a client."""
        client_requests = self.requests[client_id]
        if not client_requests:
            return time.time()
        return client_requests[0] + self.window_seconds

# Global rate limiter
rate_limiter = RateLimiter()

def get_client_id(request: Request) -> str:
    """
    Get unique client identifier from request.
    
    Args:
        request: FastAPI request object
        
    Returns:
        Unique client identifier
    """
    # Use IP address as primary identifier
    client_ip = request.client.host
    
    # Add user agent hash for additional uniqueness
    user_agent = request.headers.get("user-agent", "")
    user_agent_hash = hashlib.md5(user_agent.encode()).hexdigest()[:8]
    
    return f"{client_ip}:{user_agent_hash}"

def rate_limit(max_requests: int = 60, window_seconds: int = 60):
    """
    Decorator for rate limiting endpoints.
    
    Args:
        max_requests: Maximum requests per window
        window_seconds: Time window in seconds
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Find request object in kwargs
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            
            if request is None:
                for value in kwargs.values():
                    if isinstance(value, Request):
                        request = value
                        break
            
            if request is None:
                logger.warning("Rate limiter: No request object found")
                return await func(*args, **kwargs)
            
            client_id = get_client_id(request)
            
            # Check rate limit
            if not rate_limiter.is_allowed(client_id):
                reset_time = rate_limiter.get_reset_time(client_id)
                raise HTTPException(
                    status_code=429,
                    detail={
                        "error": "Rate limit exceeded",
                        "retry_after": int(reset_time - time.time()),
                        "limit": max_requests,
                        "window": window_seconds
                    }
                )
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator

class InputValidator:
    """Input validation for AI endpoints."""
    
    @staticmethod
    def validate_food_name(food_name: str) -> str:
        """
        Validate and sanitize food name input.
        
        Args:
            food_name: Raw food name input
            
        Returns:
            Sanitized food name
            
        Raises:
            HTTPException: If input is invalid
        """
        if not food_name or not isinstance(food_name, str):
            raise HTTPException(status_code=400, detail="Food name is required")
        
        # Remove potentially harmful characters
        sanitized = re.sub(r'[<>"\']', '', food_name.strip())
        
        if len(sanitized) < 2:
            raise HTTPException(status_code=400, detail="Food name must be at least 2 characters")
        
        if len(sanitized) > 100:
            raise HTTPException(status_code=400, detail="Food name too long (max 100 characters)")
        
        return sanitized
    
    @staticmethod
    def validate_quantity(quantity_g: float) -> float:
        """
        Validate quantity input.
        
        Args:
            quantity_g: Quantity in grams
            
        Returns:
            Validated quantity
            
        Raises:
            HTTPException: If input is invalid
        """
        if not isinstance(quantity_g, (int, float)):
            raise HTTPException(status_code=400, detail="Quantity must be a number")
        
        if quantity_g <= 0:
            raise HTTPException(status_code=400, detail="Quantity must be positive")
        
        if quantity_g > 10000:  # 10kg limit
            raise HTTPException(status_code=400, detail="Quantity too large (max 10kg)")
        
        return float(quantity_g)
    
    @staticmethod
    def validate_user_id(user_id: int) -> int:
        """
        Validate user ID input.
        
        Args:
            user_id: User ID
            
        Returns:
            Validated user ID
            
        Raises:
            HTTPException: If input is invalid
        """
        if not isinstance(user_id, int):
            raise HTTPException(status_code=400, detail="User ID must be an integer")
        
        if user_id <= 0:
            raise HTTPException(status_code=400, detail="User ID must be positive")
        
        if user_id > 1000000:  # Reasonable upper limit
            raise HTTPException(status_code=400, detail="User ID too large")
        
        return user_id
    
    @staticmethod
    def validate_query(query: str) -> str:
        """
        Validate search query input.
        
        Args:
            query: Search query
            
        Returns:
            Sanitized query
            
        Raises:
            HTTPException: If input is invalid
        """
        if not query or not isinstance(query, str):
            raise HTTPException(status_code=400, detail="Query is required")
        
        # Remove potentially harmful characters
        sanitized = re.sub(r'[<>"\']', '', query.strip())
        
        if len(sanitized) < 2:
            raise HTTPException(status_code=400, detail="Query must be at least 2 characters")
        
        if len(sanitized) > 200:
            raise HTTPException(status_code=400, detail="Query too long (max 200 characters)")
        
        return sanitized
    
    @staticmethod
    def validate_message(message: str) -> str:
        """
        Validate chat message input.
        
        Args:
            message: Chat message
            
        Returns:
            Sanitized message
            
        Raises:
            HTTPException: If input is invalid
        """
        if not message or not isinstance(message, str):
            raise HTTPException(status_code=400, detail="Message is required")
        
        # Remove potentially harmful characters but allow more flexibility
        sanitized = re.sub(r'[<>]', '', message.strip())
        
        if len(sanitized) < 1:
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        if len(sanitized) > 1000:
            raise HTTPException(status_code=400, detail="Message too long (max 1000 characters)")
        
        return sanitized

class SecurityHeaders:
    """Security headers for API responses."""
    
    @staticmethod
    def get_security_headers() -> Dict[str, str]:
        """Get security headers for API responses."""
        return {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Content-Security-Policy": "default-src 'self'"
        }

class DataSanitizer:
    """Data sanitization for sensitive information."""
    
    @staticmethod
    def sanitize_user_data(data: Dict) -> Dict:
        """
        Sanitize user data before logging or external API calls.
        
        Args:
            data: User data dictionary
            
        Returns:
            Sanitized data
        """
        sanitized = data.copy()
        
        # Remove or mask sensitive fields
        sensitive_fields = ['email', 'phone', 'address', 'ssn', 'credit_card']
        
        for field in sensitive_fields:
            if field in sanitized:
                if isinstance(sanitized[field], str) and len(sanitized[field]) > 4:
                    sanitized[field] = sanitized[field][:2] + "*" * (len(sanitized[field]) - 4) + sanitized[field][-2:]
                else:
                    sanitized[field] = "***"
        
        return sanitized
    
    @staticmethod
    def sanitize_api_response(response: Dict) -> Dict:
        """
        Sanitize API response before sending to client.
        
        Args:
            response: API response dictionary
            
        Returns:
            Sanitized response
        """
        sanitized = response.copy()
        
        # Remove internal fields
        internal_fields = ['_internal', 'debug_info', 'raw_data', 'metadata']
        
        for field in internal_fields:
            if field in sanitized:
                del sanitized[field]
        
        return sanitized

# Global instances
input_validator = InputValidator()
security_headers = SecurityHeaders()
data_sanitizer = DataSanitizer()

def add_security_headers(response):
    """Add security headers to response."""
    for key, value in security_headers.get_security_headers().items():
        response.headers[key] = value
    return response

