"""
Start command
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from .base import BaseCommand

class StartCommand(BaseCommand):
    """Start command handler"""
    
    def __init__(self, permission_manager):
        super().__init__()
        self.permission_manager = permission_manager
    
    async def execute(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user = update.effective_user
        user_id = user.id
        
        # Get user role
        role = await self.permission_manager.get_user_role(user_id)
        
        if role == "owner":
            keyboard = [
                [InlineKeyboardButton("👑 Owner Panel", callback_data="owner_panel")],
                [InlineKeyboardButton("ℹ️ Bot Info", callback_data="bot_info")]
            ]
            await update.message.reply_text(
                "👑 Owner Mode Activated",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        elif role == "admin":
            keyboard = [
                [InlineKeyboardButton("📤 Upload Videos", callback_data="start_upload")],
                [InlineKeyboardButton("📊 Statistics", callback_data="stats")],
                [InlineKeyboardButton("ℹ️ Bot Info", callback_data="bot_info")]
            ]
            await update.message.reply_text(
                "🎬 Admin Mode Activated\n\n"
                "Welcome admin! Use the buttons below to manage content.",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        else:
            keyboard = [
                [InlineKeyboardButton("ℹ️ Bot Info", callback_data="bot_info")]
            ]
            
            welcome_message = (
                "🎥 **Welcome to StreamBot!** 🤗\n\n"
                "Your ultimate destination for movies and series!\n\n"
                "🔍 Use /search to find your favorite content\n"
                "📺 Watch movies and series on demand\n"
                "🎬 Stay updated with new releases\n\n"
                "💡 Tip: Be specific in your searches for better results\n"
                "Example: `/search wednesday`\n\n"
                "📞 Need a bot like this? Contact us:\n"
                "💠 [Nova X-Code](https://t.me/Nova_king0)\n"
                "💠 [Dr internet4](https://t.me/Dr_internet4)"
            )
            
            await update.message.reply_text(
                welcome_message,
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )