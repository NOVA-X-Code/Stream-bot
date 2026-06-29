"""
Cache optimization
"""

from typing import Any, Optional, Callable
from functools import wraps
from datetime import datetime, timedelta
import asyncio

class OptimizedCache:
    """Optimized cache with TTL"""
    
    def __init__(self, default_ttl: int = 300):
        self.cache = {}
        self.default_ttl = default_ttl
        self._lock = asyncio.Lock()
    
    def get(self, key: str) -> Optional[Any]:
        """Get cached value"""
        entry = self.cache.get(key)
        if not entry:
            return None
        
        value, timestamp, ttl = entry
        if (datetime.now() - timestamp).seconds > ttl:
            self.cache.pop(key, None)
            return None
        
        return value
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set cache value"""
        self.cache[key] = (value, datetime.now(), ttl or self.default_ttl)
    
    def clear(self):
        """Clear cache"""
        self.cache.clear()

def cached(ttl: int = 300):
    """Cache decorator"""
    cache = OptimizedCache(ttl)
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            
            cached_result = cache.get(key)
            if cached_result is not None:
                return cached_result
            
            result = await func(*args, **kwargs)
            cache.set(key, result)
            return result
        return wrapper
    return decorator
