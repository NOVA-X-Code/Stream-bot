"""
Main entry point for the Telegram bot
"""

import os
import sys
import logging
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

from telegram import Update
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ConversationHandler,
)

from .config import Config
from .database.supabase_client import SupabaseClient
from .commands import (
    StartCommand,
    SearchCommand,
    UploadCommand,
    AddAdminCommand,
    ListAdminsCommand,
    StatsCommand,
    HelpCommand,
)
from .services import VideoService, AdminService, StatsService, SearchService
from .services.validation_service import ValidationService
from .security import PermissionManager, RateLimiter, AuditLogger
from .security.middleware import BotMiddleware, LoggingMiddleware, RateLimiterMiddleware

# Setup logging
logger = logging.getLogger(__name__)

class HealthCheckHandler(BaseHTTPRequestHandler):
    """Health check endpoint for container orchestration"""
    
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'OK')
        else:
            self.send_response(404)
            self.end_headers()

def start_health_server(port: int = 8080):
    """Start health check server"""
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    logger.info(f"Health check server running on port {port}")
    server.serve_forever()

def main():
    """Main entry point"""
    try:
        # Initialize configuration
        config = Config()
        logger.info("Configuration loaded successfully")
        
        # Initialize Supabase client
        supabase = SupabaseClient(
            config.SUPABASE_URL,
            config.SUPABASE_KEY
        )
        logger.info("Supabase client initialized")
        
        # Initialize services
        permission_manager = PermissionManager(supabase)
        rate_limiter = RateLimiter()
        audit_logger = AuditLogger(supabase)
        
        video_service = VideoService(supabase)
        admin_service = AdminService(supabase, permission_manager)
        search_service = SearchService(supabase)
        stats_service = StatsService(supabase)
        validation_service = ValidationService()
        
        # Create bot application
        application = ApplicationBuilder() \
            .token(config.TELEGRAM_TOKEN) \
            .build()
        
        # Setup middleware
        middleware = BotMiddleware()
        middleware.register(LoggingMiddleware())
        middleware.register(RateLimiterMiddleware(rate_limiter))
        
        # Register commands
        application.add_handler(CommandHandler("start", StartCommand(permission_manager).execute))
        application.add_handler(CommandHandler("help", HelpCommand().execute))
        application.add_handler(CommandHandler("search", SearchCommand(search_service).execute))
        application.add_handler(CommandHandler("stats", StatsCommand(stats_service, video_service).execute))
        
        # Admin commands
        application.add_handler(CommandHandler("addadmin", AddAdminCommand(admin_service).execute))
        application.add_handler(CommandHandler("listadmins", ListAdminsCommand(admin_service).execute))
        
        # Upload conversation
        upload_handler = UploadCommand(video_service, validation_service, permission_manager)
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler("upload", upload_handler.execute)],
            states={
                upload_handler.WAITING_VIDEO: [
                    MessageHandler(filters.VIDEO, upload_handler.handle_video),
                    CommandHandler("done", upload_handler.done),
                    CommandHandler("status", upload_handler.status),
                    CommandHandler("cancel", upload_handler.cancel),
                ],
            },
            fallbacks=[CommandHandler("cancel", upload_handler.cancel)],
        )
        application.add_handler(conv_handler)
        
        # Start health check server in background
        health_thread = threading.Thread(
            target=start_health_server,
            args=(config.PORT,),
            daemon=True
        )
        health_thread.start()
        
        # Start the bot
        logger.info("Starting Telegram bot...")
        application.run_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True
        )
        
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()