"""
Supabase client with advanced features
"""

from typing import Optional, List, Dict, Any
from supabase import create_client, Client
from datetime import datetime
import json
import asyncio

class SupabaseClient:
    """
    Enhanced Supabase client with caching and retry logic
    """
    
    def __init__(self, url: str, key: str):
        self.client = create_client(url, key)
        self._cache = {}
        self._max_retries = 3
    
    async def execute_with_retry(self, query_func, *args, **kwargs):
        """Execute query with retry logic"""
        for attempt in range(self._max_retries):
            try:
                return await query_func(*args, **kwargs)
            except Exception as e:
                if attempt == self._max_retries - 1:
                    raise
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
    
    class Table:
        """Fluent interface for table operations"""
        
        def __init__(self, client: Client, table_name: str):
            self.client = client
            self.table_name = table_name
            self._select = '*'
            self._filters = []
            self._order = None
            self._limit = None
            self._offset = None
        
        def select(self, columns: str = '*'):
            self._select = columns
            return self
        
        def eq(self, column: str, value: Any):
            self._filters.append(('eq', column, value))
            return self
        
        def neq(self, column: str, value: Any):
            self._filters.append(('neq', column, value))
            return self
        
        def gt(self, column: str, value: Any):
            self._filters.append(('gt', column, value))
            return self
        
        def lt(self, column: str, value: Any):
            self._filters.append(('lt', column, value))
            return self
        
        def contains(self, column: str, value: list):
            self._filters.append(('contains', column, value))
            return self
        
        def in_(self, column: str, value: list):
            self._filters.append(('in', column, value))
            return self
        
        def order(self, column: str, ascending: bool = True):
            self._order = (column, ascending)
            return self
        
        def limit(self, limit: int):
            self._limit = limit
            return self
        
        def offset(self, offset: int):
            self._offset = offset
            return self
        
        async def execute(self) -> List[dict]:
            """Execute the built query"""
            query = self.client.table(self.table_name).select(self._select)
            
            # Apply filters
            for filter_type, column, value in self._filters:
                if filter_type == 'eq':
                    query = query.eq(column, value)
                elif filter_type == 'neq':
                    query = query.neq(column, value)
                elif filter_type == 'gt':
                    query = query.gt(column, value)
                elif filter_type == 'lt':
                    query = query.lt(column, value)
                elif filter_type == 'contains':
                    query = query.contains(column, value)
                elif filter_type == 'in':
                    query = query.in_(column, value)
            
            # Apply ordering
            if self._order:
                query = query.order(self._order[0], desc=not self._order[1])
            
            # Apply limit
            if self._limit:
                query = query.limit(self._limit)
            
            # Apply offset
            if self._offset:
                query = query.offset(self._offset)
            
            return query.execute().data
        
        async def insert(self, data: dict) -> dict:
            """Insert a single record"""
            result = self.client.table(self.table_name).insert(data).execute()
            return result.data[0] if result.data else None
        
        async def insert_many(self, data: List[dict]) -> List[dict]:
            """Insert multiple records"""
            result = self.client.table(self.table_name).insert(data).execute()
            return result.data
        
        async def update(self, data: dict) -> dict:
            """Update records"""
            query = self.client.table(self.table_name).update(data)
            
            # Apply filters
            for filter_type, column, value in self._filters:
                if filter_type == 'eq':
                    query = query.eq(column, value)
            
            result = query.execute()
            return result.data[0] if result.data else None
        
        async def delete(self) -> int:
            """Delete records"""
            query = self.client.table(self.table_name).delete()
            
            # Apply filters
            for filter_type, column, value in self._filters:
                if filter_type == 'eq':
                    query = query.eq(column, value)
            
            result = query.execute()
            return len(result.data)
    
    def table(self, name: str) -> Table:
        """Get a table query builder"""
        return self.Table(self.client, name)
    
    async def rpc(self, function_name: str, params: dict = None) -> Any:
        """Execute a stored procedure"""
        result = self.client.rpc(function_name, params or {}).execute()
        return result.data