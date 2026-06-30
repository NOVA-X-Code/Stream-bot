"""
Permission management system
"""

from enum import Enum
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

class Permission(Enum):
    """Available permissions"""
    VIEW = "view"
    SEARCH = "search"
    UPLOAD = "upload"
    DELETE = "delete"
    MANAGE_ADMINS = "manage_admins"
    MANAGE_CHANNELS = "manage_channels"
    VIEW_STATS = "view_stats"
    MANAGE_USERS = "manage_users"

class Role(Enum):
    """User roles with permissions"""
    USER = "user"
    ADMIN = "admin"
    OWNER = "owner"
    
    def get_permissions(self) -> List[Permission]:
        """Get permissions for this role"""
        permissions = {
            Role.USER: [Permission.VIEW, Permission.SEARCH],
            Role.ADMIN: [
                Permission.VIEW, Permission.SEARCH,
                Permission.UPLOAD, Permission.DELETE,
                Permission.VIEW_STATS
            ],
            Role.OWNER: list(Permission)
        }
        return permissions.get(self, [])

class PermissionManager:
    """Permission manager with caching"""
    
    def __init__(self, supabase_client):
        self.supabase = supabase_client
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes
    
    async def get_user_role(self, user_id: int) -> Role:
        """Get user role with caching"""
        # Check cache
        if user_id in self.cache:
            role, timestamp = self.cache[user_id]
            if (datetime.now() - timestamp).seconds < self.cache_ttl:
                return role
        
        # Check database
        result = self.supabase.table('admins').select('*').eq('user_id', user_id).execute()
        
        if result:
            role = Role.ADMIN
        else:
            role = Role.USER
        
        # Cache result
        self.cache[user_id] = (role, datetime.now())
        
        return role
    
    async def can_upload(self, user_id: int) -> bool:
        """Check if user can upload"""
        role = await self.get_user_role(user_id)
        return Permission.UPLOAD in role.get_permissions()
    
    async def can_manage_admins(self, user_id: int) -> bool:
        """Check if user can manage admins"""
        role = await self.get_user_role(user_id)
        return Permission.MANAGE_ADMINS in role.get_permissions()