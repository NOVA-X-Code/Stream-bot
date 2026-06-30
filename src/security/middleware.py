"""
Bot middleware system
"""

from typing import Callable
from telegram import Update
from telegram.ext import ContextTypes
import logging

logger = logging.getLogger(__name__)

class BotMiddleware:
    """Middleware manager"""
    
    def __init__(self):
        self.handlers = []
    
    def register(self, handler: Callable):
        """Register middleware handler"""
        self.handlers.append(handler)
    
    async def process(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Process through all middlewares"""
        for handler in self.handlers:
            await handler(update, context)

class LoggingMiddleware:
    """Logging middleware"""
    
    async def __call__(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        if user:
            logger.info(
                f"📨 Message from {user.username or user.id}: "
                f"{update.message.text if update.message else '...'}"
            )

class RateLimiterMiddleware:
    """Rate limiting middleware"""
    
    def __init__(self, rate_limiter):
        self.rate_limiter = rate_limiter
    
    async def __call__(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        # Rate limiting logic here
        pass