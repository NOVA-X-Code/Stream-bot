"""
Performance tests
"""

import pytest
import asyncio
import time

class PerformanceTest:
    """Performance testing utilities"""
    
    @staticmethod
    async def measure_time(func, *args, **kwargs):
        """Measure function execution time"""
        start = time.time()
        result = await func(*args, **kwargs)
        duration = time.time() - start
        return result, duration
    
    @staticmethod
    async def stress_test(func, iterations: int = 100):
        """Stress test a function"""
        start = time.time()
        results = []
        errors = []
        
        for _ in range(iterations):
            try:
                result = await func()
                results.append(result)
            except Exception as e:
                errors.append(str(e))
        
        duration = time.time() - start
        
        return {
            'total_iterations': iterations,
            'successful': len(results),
            'failed': len(errors),
            'duration': duration,
            'average_time': duration / iterations
        }

@pytest.mark.asyncio
async def test_search_performance():
    """Test search performance"""
    from src.services.search_service import SearchService
    from src.database.supabase_client import SupabaseClient
    
    # Mock Supabase
    supabase = Mock(spec=SupabaseClient)
    search_service = SearchService(supabase)
    
    test = PerformanceTest()
    result, duration = await test.measure_time(
        search_service.search,
        query="test"
    )
    
    assert duration < 2.0  # Less than 2 seconds