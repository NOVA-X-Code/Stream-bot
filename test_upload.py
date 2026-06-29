"""
Upload tests
"""

import pytest
from unittest.mock import Mock, AsyncMock

@pytest.mark.asyncio
async def test_upload_validation():
    """Test upload validation"""
    from src.services.validation_service import ValidationService
    
    service = ValidationService()
    
    # Test valid video
    video = Mock()
    video.file_size = 10 * 1024 * 1024  # 10MB
    video.duration = 300
    video.mime_type = "video/mp4"
    
    is_valid, errors = await service.validate_video(video)
    assert is_valid
    assert len(errors) == 0
    
    # Test invalid video
    video.file_size = 60 * 1024 * 1024  # 60MB
    is_valid, errors = await service.validate_video(video)
    assert not is_valid
    assert len(errors) > 0