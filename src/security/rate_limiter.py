"""
Rate limiting system
"""

from typing import Dict, List, Tuple
from datetime import datetime, timedelta
import asyncio
from collections import defaultdict

class SlidingWindowRateLimiter:
    """Rate limiter with sliding window"""
    
    def __init__(self, max_requests: int = 30, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[int, List[datetime]] = defaultdict(list)
        self._lock = asyncio.Lock()
    
    async def is_allowed(self, user_id: int) -> bool:
        """Check if request is allowed"""
        async with self._lock:
            now = datetime.now()
            window_start = now - timedelta(seconds=self.window_seconds)
            
            # Clean old requests
            self.requests[user_id] = [
                req for req in self.requests[user_id]
                if req > window_start
            ]
            
            # Check limit
            if len(self.requests[user_id]) >= self.max_requests:
                return False
            
            # Add request
            self.requests[user_id].append(now)
            return True
    
    async def get_remaining(self, user_id: int) -> Tuple[int, int]:
        """Get remaining requests and wait time"""
        async with self._lock:
            now = datetime.now()
            window_start = now - timedelta(seconds=self.window_seconds)
            
            # Clean old requests
            self.requests[user_id] = [
                req for req in self.requests[user_id]
                if req > window_start
            ]
            
            remaining = self.max_requests - len(self.requests[user_id])
            
            if remaining <= 0:
                oldest = min(self.requests[user_id])
                wait_time = (oldest + timedelta(seconds=self.window_seconds) - now).seconds
            else:
                wait_time = 0
            
            return remaining, wait_time

class RateLimiter:
    """Multi-level rate limiter"""
    
    def __init__(self):
        self.limiters = {
            'user': SlidingWindowRateLimiter(30, 60),
            'admin': SlidingWindowRateLimiter(60, 60),
            'owner': SlidingWindowRateLimiter(120, 60)
        }
    
    async def is_allowed(self, user_id: int, role: str = 'user') -> bool:
        """Check if user is allowed based on role"""
        limiter = self.limiters.get(role, self.limiters['user'])
        return await limiter.is_allowed(user_id)
