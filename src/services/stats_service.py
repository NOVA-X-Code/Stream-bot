"""
Statistics service
"""

from typing import Dict, Any
from datetime import datetime, timedelta

class StatsService:
    """Statistics service"""
    
    def __init__(self, supabase_client):
        self.client = supabase_client
    
    async def get_total_videos(self) -> int:
        """Get total video count"""
        result = await self.client.table('videos').select('count').execute()
        return result[0]['count'] if result else 0
    
    async def get_total_users(self) -> int:
        """Get total user count"""
        result = await self.client.table('users').select('count').execute()
        return result[0]['count'] if result else 0
    
    async def get_total_admins(self) -> int:
        """Get total admin count"""
        result = await self.client.table('admins').select('count').execute()
        return result[0]['count'] if result else 0
    
    async def get_total_views(self) -> int:
        """Get total views"""
        result = await self.client.table('videos').select('views').execute()
        return sum(video.get('views', 0) for video in result)
    
    async def get_recent_activity(self, hours: int = 24) -> Dict[str, int]:
        """Get recent activity stats"""
        since = (datetime.now() - timedelta(hours=hours)).isoformat()
        
        # Count uploads
        uploads = await self.client.table('videos') \
            .select('count') \
            .gte('upload_date', since) \
            .execute()
        
        # Count searches
        searches = await self.client.table('audit_logs') \
            .select('count') \
            .eq('action', 'search') \
            .gte('timestamp', since) \
            .execute()
        
        return {
            'uploads': uploads[0]['count'] if uploads else 0,
            'searches': searches[0]['count'] if searches else 0,
            'views': 0  # Would need separate tracking
        }