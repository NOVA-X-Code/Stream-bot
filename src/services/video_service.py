"""
Video service
"""

from typing import List, Optional
from datetime import datetime
from ..models.video import Video

class VideoService:
    """Video management service"""
    
    def __init__(self, supabase_client):
        self.client = supabase_client
    
    def create_video(self, file_id: str, caption: str, owner_id: int, 
                     owner_username: str, duration: int, file_size: int) -> Video:
        """Create a video object"""
        return Video(
            file_id=file_id,
            caption=caption,
            owner_id=owner_id,
            owner_username=owner_username,
            duration=duration,
            file_size=file_size,
            upload_date=datetime.now()
        )
    
    async def save_videos(self, videos: List[Video]) -> int:
        """Save multiple videos"""
        if not videos:
            return 0
        
        data = []
        for video in videos:
            data.append({
                'file_id': video.file_id,
                'caption': video.caption,
                'tags': video.tags,
                'owner_id': video.owner_id,
                'owner_username': video.owner_username,
                'duration': video.duration,
                'file_size': video.file_size,
                'upload_date': video.upload_date.isoformat()
            })
        
        result = await self.client.table('videos').insert(data).execute()
        return len(result)
    
    async def get_most_viewed(self, limit: int = 3) -> List[Video]:
        """Get most viewed videos"""
        result = await self.client.table('videos') \
            .select('*') \
            .order('views', ascending=False) \
            .limit(limit) \
            .execute()
        
        return [Video(**data) for data in result]
