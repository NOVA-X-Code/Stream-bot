"""
Upload command with conversation flow
"""

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from .base import BaseCommand

class UploadCommand(BaseCommand):
    """Upload command with conversation management"""
    
    WAITING_VIDEO = 1
    
    def __init__(self, video_service, validation_service, permission_manager):
        super().__init__()
        self.video_service = video_service
        self.validation_service = validation_service
        self.permission_manager = permission_manager
    
    async def check_permission(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """Check if user can upload"""
        user_id = update.effective_user.id
        return await self.permission_manager.can_upload(user_id)
    
    async def execute(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start upload process"""
        user_id = update.effective_user.id
        
        if not await self.check_permission(update, context):
            await update.message.reply_text("⛔ You don't have upload permissions")
            return ConversationHandler.END
        
        context.user_data['upload'] = {
            'videos': [],
            'current': None
        }
        
        await update.message.reply_text(
            "📤 **Upload Mode Activated**\n\n"
            "Send videos one by one.\n"
            "You can add a caption with each video.\n\n"
            "📝 Commands:\n"
            "- `/done` to finish\n"
            "- `/cancel` to cancel\n"
            "- `/status` to see progress\n\n"
            "📊 Max: 5 videos per session",
            parse_mode="Markdown"
        )
        
        return self.WAITING_VIDEO
    
    async def handle_video(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle received video"""
        video = update.message.video
        caption = update.message.caption or ""
        
        # Validate video
        is_valid, errors = await self.validation_service.validate_video(video)
        
        if not is_valid:
            error_msg = "❌ **Validation Errors:**\n\n" + "\n".join(f"• {e}" for e in errors)
            await update.message.reply_text(error_msg, parse_mode="Markdown")
            return self.WAITING_VIDEO
        
        # Check upload limit
        if len(context.user_data['upload']['videos']) >= 5:
            await update.message.reply_text("⚠️ Maximum 5 videos per session. Type /done to finish.")
            return self.WAITING_VIDEO
        
        # Create video object
        video_obj = self.video_service.create_video(
            file_id=video.file_id,
            caption=caption,
            owner_id=update.effective_user.id,
            owner_username=update.effective_user.username,
            duration=video.duration,
            file_size=video.file_size
        )
        
        # Add to session
        context.user_data['upload']['videos'].append(video_obj)
        
        await update.message.reply_text(
            f"✅ **Video Added!**\n\n"
            f"📝 Caption: {caption or 'None'}\n"
            f"📊 Size: {video.file_size / 1024 / 1024:.1f} MB\n"
            f"⏱️ Duration: {video.duration}s\n"
            f"📦 Total: {len(context.user_data['upload']['videos'])}/5 videos\n\n"
            "Send another or type `/done` to finish.",
            parse_mode="Markdown"
        )
        
        return self.WAITING_VIDEO
    
    async def done(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Finish upload process"""
        videos = context.user_data.get('upload', {}).get('videos', [])
        
        if not videos:
            await update.message.reply_text("⚠️ No videos to upload.")
            return self.WAITING_VIDEO
        
        # Save videos
        saved = await self.video_service.save_videos(videos)
        
        # Cleanup
        context.user_data.pop('upload', None)
        
        await update.message.reply_text(
            f"✅ **{saved} video(s) saved successfully!**\n\n"
            "Thank you for your contribution! 🎉",
            parse_mode="Markdown"
        )
        
        return ConversationHandler.END
    
    async def status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show upload status"""
        videos = context.user_data.get('upload', {}).get('videos', [])
        
        if not videos:
            await update.message.reply_text("📭 No videos in upload queue")
            return self.WAITING_VIDEO
        
        status_msg = f"📊 **Upload Status**\n\n📦 Total: {len(videos)}/5 videos\n\n"
        
        for i, video in enumerate(videos, 1):
            status_msg += f"{i}. {video.caption or 'Untitled'} "
            status_msg += f"({video.file_size / 1024 / 1024:.1f} MB)\n"
        
        await update.message.reply_text(status_msg, parse_mode="Markdown")
        return self.WAITING_VIDEO
    
    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Cancel upload process"""
        context.user_data.pop('upload', None)
        await update.message.reply_text("❌ Upload cancelled.")
        return ConversationHandler.END