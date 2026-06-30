"""
Admin service
"""

from typing import List, Optional
from datetime import datetime

class AdminService:
    """Admin management service"""
    
    def __init__(self, supabase_client, permission_manager):
        self.client = supabase_client
        self.permission_manager = permission_manager
    
    async def is_owner(self, user_id: int) -> bool:
        """Check if user is owner"""
        # Check if user is the owner
        from ..config import Config
        config = Config()
        return user_id == config.OWNER_ID
    
    async def is_admin(self, user_id: int) -> bool:
        """Check if user is admin"""
        result = await self.client.table('admins') \
            .select('*') \
            .eq('user_id', user_id) \
            .execute()
        return bool(result)
    
    async def add_admin(self, user_id: int, username: str, added_by: int):
        """Add a new admin"""
        data = {
            'user_id': user_id,
            'username': username,
            'added_by': added_by,
            'added_at': datetime.now().isoformat(),
            'is_active': True
        }
        
        result = await self.client.table('admins').insert(data).execute()
        return result[0] if result else None
    
    async def get_all_admins(self) -> List:
        """Get all admins"""
        result = await self.client.table('admins') \
            .select('*') \
            .order('added_at', ascending=True) \
            .execute()
        return result