"""
Search service
"""

from typing import List, Optional
from ..models.video import Video

class SearchService:
    """Video search service"""
    
    def __init__(self, supabase_client):
        self.client = supabase_client
    
    async def search(
        self,
        query: str,
        genre: Optional[str] = None,
        year: Optional[int] = None,
        limit: int = 5
    ) -> List[Video]:
        """Search videos with filters"""
        # Build query
        search_query = self.client.table('videos').select('*')
        
        # Add filters
        if query:
            search_query = search_query.ilike('caption', f'%{query}%')
        
        if genre:
            search_query = search_query.contains('tags', [genre])
        
        if year:
            search_query = search_query.eq('upload_date', f'{year}-%')
        
        # Execute
        result = await search_query \
            .order('views', ascending=False) \
            .limit(limit) \
            .execute()
        
        return [Video(**data) for data in result]