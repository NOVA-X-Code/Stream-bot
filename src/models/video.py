"""
Video model
"""

from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime

@dataclass
class Video:
    """Video model"""
    
    file_id: str
    caption: Optional[str] = None
    tags: List[str] = None
    owner_id: Optional[int] = None
    owner_username: Optional[str] = None
    duration: Optional[int] = None
    file_size: Optional[int] = None
    views: int = 0
    upload_date: datetime = datetime.now()
    id: Optional[int] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
    
    @property
    def size_mb(self) -> float:
        """Size in MB"""
        if self.file_size:
            return self.file_size / (1024 * 1024)
        return 0
    
    def add_tag(self, tag: str) -> None:
        """Add a tag"""
        if tag not in self.tags:
            self.tags.append(tag)
    
    def to_dict(self) -> dict:
        """Convert to dict"""
        return {
            'file_id': self.file_id,
            'caption': self.caption,
            'tags': self.tags,
            'owner_id': self.owner_id,
            'owner_username': self.owner_username,
            'duration': self.duration,
            'file_size': self.file_size,
            'views': self.views,
            'upload_date': self.upload_date.isoformat()
        }
