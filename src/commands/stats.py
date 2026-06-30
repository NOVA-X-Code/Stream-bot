"""
Statistics command
"""

from telegram import Update
from telegram.ext import ContextTypes
from .base import BaseCommand

class StatsCommand(BaseCommand):
    """Statistics command"""
    
    def __init__(self, stats_service, video_service):
        super().__init__()
        self.stats_service = stats_service
        self.video_service = video_service
    
    async def execute(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show bot statistics"""
        
        # Get stats
        total_videos = await self.stats_service.get_total_videos()
        total_users = await self.stats_service.get_total_users()
        total_admins = await self.stats_service.get_total_admins()
        total_views = await self.stats_service.get_total_views()
        
        top_videos = await self.video_service.get_most_viewed(limit=3)
        recent_activity = await self.stats_service.get_recent_activity(hours=24)
        
        message = (
            "📊 **Bot Statistics**\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            f"🎬 **Videos:** {total_videos}\n"
            f"👤 **Users:** {total_users}\n"
            f"👑 **Admins:** {total_admins}\n"
            f"👀 **Total Views:** {total_views:,}\n\n"
        )
        
        if top_videos:
            message += "🏆 **Top Videos:**\n"
            for i, video in enumerate(top_videos, 1):
                message += f"{i}. {video.caption[:30]}... ({video.views} views)\n"
            message += "\n"
        
        message += (
            f"📈 **Activity (24h):**\n"
            f"📤 Uploads: {recent_activity.get('uploads', 0)}\n"
            f"🔍 Searches: {recent_activity.get('searches', 0)}\n"
            f"👀 Views: {recent_activity.get('views', 0)}\n"
        )
        
        await update.message.reply_text(message, parse_mode="Markdown")