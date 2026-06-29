"""
Search tests
"""

import pytest
from unittest.mock import Mock, AsyncMock

@pytest.mark.asyncio
async def test_search_command():
    """Test search command"""
    from src.commands.search import SearchCommand
    from src.services.search_service import SearchService
    
    # Mock service
    search_service = Mock(spec=SearchService)
    search_service.search = AsyncMock(return_value=[])
    
    command = SearchCommand(search_service)
    
    # Test execution
    update = Mock()
    update.message = Mock()
    context = Mock()
    context.args = ["test"]
    
    await command.execute(update, context)
    
    search_service.search.assert_called_once_with(
        query="test",
        genre=None,
        year=None,
        limit=5
    )