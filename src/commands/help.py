"""
Help command
"""

from telegram import Update
from telegram.ext import ContextTypes
from .base import BaseCommand

class HelpCommand(BaseCommand):
    """Help command"""
    
    async def execute(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show help message"""
        help_text = (
            "📚 **Available Commands**\n\n"
            "**General**\n"
            "/start - Welcome message\n"
            "/help - Show this help\n"
            "/search <query> - Search videos\n"
            "/stats - Show bot statistics\n\n"
            "**Admin**\n"
            "/upload - Upload videos\n"
            "/addadmin @username - Add admin\n"
            "/listadmins - List admins\n"
        )
        
        await update.message.reply_text(help_text, parse_mode="Markdown")