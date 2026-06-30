"""
Search command with advanced filtering
"""

from typing import List
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from .base import BaseCommand

class SearchCommand(BaseCommand):
    """Advanced search command"""
    
    def __init__(self, search_service):
        super().__init__()
        self.search_service = search_service
    
    async def execute(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /search command"""
        query = ' '.join(context.args)
        
        if not query:
            await update.message.reply_text(
                "🔍 **Search Videos**\n\n"
                "Usage: `/search <keyword>`\n"
                "Example: `/search wednesday`\n\n"
                "💡 **Tips:**\n"
                "- Use specific keywords\n"
                "- Try genres: action, comedy, drama, etc.\n"
                "- Add year: `/search action 2024`",
                parse_mode="Markdown"
            )
            return
        
        # Parse filters
        filters = self._parse_filters(query)
        results = await self.search_service.search(
            query=filters['query'],
            genre=filters['genre'],
            year=filters['year'],
            limit=5
        )
        
        if not results:
            await update.message.reply_text(
                f"🔍 No results found for: `{query}`\n\n"
                "💡 Try:\n"
                "- Different keywords\n"
                "- Alternative spelling\n"
                "- Removing filters",
                parse_mode="Markdown"
            )
            return
        
        await self._send_results(update, context, results)
    
    def _parse_filters(self, query: str) -> dict:
        """Parse search filters from query"""
        parts = query.lower().split()
        filters = {
            'query': [],
            'genre': None,
            'year': None
        }
        
        genres = ['action', 'comedy', 'drama', 'horror', 'thriller', 
                  'sci-fi', 'romance', 'adventure', 'fantasy']
        
        for part in parts:
            if part in genres:
                filters['genre'] = part
            elif part.isdigit() and len(part) == 4:
                filters['year'] = int(part)
            else:
                filters['query'].append(part)
        
        filters['query'] = ' '.join(filters['query'])
        return filters
    
    async def _send_results(self, update: Update, context: ContextTypes.DEFAULT_TYPE, videos: List):
        """Send search results with interactive buttons"""
        for i, video in enumerate(videos, 1):
            keyboard = [
                [
                    InlineKeyboardButton("▶️ Watch", callback_data=f"watch_{video.id}"),
                    InlineKeyboardButton("ℹ️ Details", callback_data=f"details_{video.id}")
                ]
            ]
            
            caption = (
                f"**🎬 {i}. {video.caption or 'Untitled'}**\n"
                f"🏷️ Tags: {', '.join(video.tags) if video.tags else 'None'}\n"
                f"📅 Added: {video.upload_date.strftime('%d/%m/%Y')}\n"
                f"👤 By: @{video.owner_username or 'Unknown'}\n"
                f"📊 Views: {video.views}"
            )
            
            await context.bot.send_video(
                chat_id=update.effective_chat.id,
                video=video.file_id,
                caption=caption,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="Markdown"
            )
            
            # Avoid rate limiting
            if i < len(videos):
                import asyncio
                await asyncio.sleep(0.5)