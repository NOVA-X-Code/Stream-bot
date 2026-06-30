"""
Advanced async patterns
"""

import asyncio
from typing import List, Any, Callable
from contextlib import asynccontextmanager

class AsyncPool:
    """Async connection pool"""
    
    def __init__(self, create_connection, max_size: int = 10):
        self.create_connection = create_connection
        self.max_size = max_size
        self.pool = []
        self._lock = asyncio.Lock()
    
    @asynccontextmanager
    async def get_connection(self):
        """Get connection from pool"""
        async with self._lock:
            if self.pool:
                conn = self.pool.pop()
            else:
                conn = await self.create_connection()
        
        try:
            yield conn
        finally:
            async with self._lock:
                if len(self.pool) < self.max_size:
                    self.pool.append(conn)

class Throttle:
    """Concurrency throttle"""
    
    def __init__(self, max_concurrent: int):
        self.semaphore = asyncio.Semaphore(max_concurrent)
    
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """Call function with concurrency limit"""
        async with self.semaphore:
            return await func(*args, **kwargs)

class AsyncPipeline:
    """Async pipeline"""
    
    def __init__(self):
        self.stages = []
    
    def add_stage(self, stage: Callable):
        """Add pipeline stage"""
        self.stages.append(stage)
    
    async def process(self, initial_data: Any) -> Any:
        """Process through pipeline"""
        data = initial_data
        for stage in self.stages:
            data = await stage(data)
        return data