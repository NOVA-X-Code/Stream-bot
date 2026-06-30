"""
Audit logging system
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

class AuditLogger:
    """Audit logging system"""
    
    def __init__(self, supabase_client):
        self.supabase = supabase_client
    
    async def log_action(
        self,
        user_id: int,
        action: str,
        details: Dict[str, Any],
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ):
        """Log user action"""
        log_entry = {
            'user_id': user_id,
            'action': action,
            'details': details,
            'ip_address': ip_address,
            'user_agent': user_agent,
            'timestamp': datetime.now().isoformat()
        }
        
        await self.supabase.table('audit_logs').insert(log_entry).execute()
    
    async def get_user_actions(
        self,
        user_id: int,
        limit: int = 50,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Get user actions with date filtering"""
        query = self.supabase.table('audit_logs') \
            .select('*') \
            .eq('user_id', user_id) \
            .order('timestamp', desc=True) \
            .limit(limit)
        
        if start_date:
            query = query.gte('timestamp', start_date.isoformat())
        if end_date:
            query = query.lte('timestamp', end_date.isoformat())
        
        result = await query.execute()
        return result