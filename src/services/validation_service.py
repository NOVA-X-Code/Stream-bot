"""
Validation service
"""

from typing import Tuple, List
from ..config import Config

class ValidationService:
    """Video validation service"""
    
    def __init__(self):
        self.config = Config()
    
    async def validate_video(self, video) -> Tuple[bool, List[str]]:
        """Validate a video"""
        errors = []
        
        # Check size
        if video.file_size > self.config.MAX_VIDEO_SIZE_MB * 1024 * 1024:
            errors.append(f"Video exceeds {self.config.MAX_VIDEO_SIZE_MB}MB limit")
        
        # Check duration
        if video.duration and video.duration > self.config.MAX_VIDEO_DURATION_SECONDS:
            errors.append(f"Video exceeds {self.config.MAX_VIDEO_DURATION_SECONDS} seconds")
        
        # Check format
        if video.mime_type and not video.mime_type.startswith('video/'):
            errors.append("Invalid video format")
        
        return len(errors) == 0, errors