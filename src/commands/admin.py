"""
Administration commands
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from .base import BaseCommand

class AddAdminCommand(BaseCommand):
    """Add administrator command"""
    
    def __init__(self, admin_service):
        super().__init__()
        self.admin_service = admin_service
    
    async def check_permission(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """Only owner can add admins"""
        user_id = update.effective_user.id
        return await self.admin_service.is_owner(user_id)
    
    async def execute(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Add a new administrator"""
        if not context.args:
            await update.message.reply_text(
                "📝 **Add Administrator**\n\n"
                "Usage: `/addadmin @username`\n"
                "Example: `/addadmin @john_doe`\n\n"
                "⚠️ User must have interacted with the bot.",
                parse_mode="Markdown"
            )
            return
        
        username = context.args[0].strip('@')
        
        try:
            user = await context.bot.get_chat(f"@{username}")
            
            admin = await self.admin_service.add_admin(
                user_id=user.id,
                username=username,
                added_by=update.effective_user.id
            )
            
            await update.message.reply_text(
                f"✅ **Admin Added!**\n\n"
                f"👤 User: @{username}\n"
                f"🆔 ID: {user.id}\n"
                f"📅 Added: {admin.added_at.strftime('%d/%m/%Y at %H:%M')}\n\n"
                "User now has admin privileges.",
                parse_mode="Markdown"
            )
        except Exception as e:
            await update.message.reply_text(
                f"❌ **Error:** {str(e)}\n\n"
                "Make sure:\n"
                "1. Username is correct\n"
                "2. User has interacted with the bot\n"
                "3. User is not already an admin"
            )

class ListAdminsCommand(BaseCommand):
    """List administrators command"""
    
    def __init__(self, admin_service):
        super().__init__()
        self.admin_service = admin_service
    
    async def check_permission(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """Only admins can list admins"""
        user_id = update.effective_user.id
        return await self.admin_service.is_admin(user_id)
    
    async def execute(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """List all administrators"""
        admins = await self.admin_service.get_all_admins()
        
        if not admins:
            await update.message.reply_text("📭 No administrators found")
            return
        
        # Pagination
        page = int(context.args[0]) - 1 if context.args and context.args[0].isdigit() else 0
        per_page = 10
        total_pages = (len(admins) + per_page - 1) // per_page
        
        if page >= total_pages:
            page = total_pages - 1
        
        start = page * per_page
        end = min(start + per_page, len(admins))
        
        message = "👥 **Administrators**\n\n"
        message += f"Page {page + 1}/{total_pages}\n"
        message += "━━━━━━━━━━━━━━━━━━\n\n"
        
        for i, admin in enumerate(admins[start:end], start + 1):
            message += f"{i}. @{admin.username}\n"
            message += f"   🆔 ID: {admin.user_id}\n"
            message += f"   📅 Added: {admin.added_at.strftime('%d/%m/%Y')}\n"
            if admin.channel_links:
                message += f"   📢 Channels: {len(admin.channel_links)}\n"
            message += "\n"
        
        # Pagination buttons
        keyboard = []
        if total_pages > 1:
            row = []
            if page > 0:
                row.append(InlineKeyboardButton("◀️ Previous", callback_data=f"admin_page_{page-1}"))
            if page < total_pages - 1:
                row.append(InlineKeyboardButton("Next ▶️", callback_data=f"admin_page_{page+1}"))
            keyboard.append(row)
        
        if keyboard:
            await update.message.reply_text(
                message,
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        else:
            await update.message.reply_text(message, parse_mode="Markdown")