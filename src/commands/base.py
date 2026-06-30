"""
Base command class
"""

from abc import ABC, abstractmethod
from typing import Any, Optional
from telegram import Update
from telegram.ext import ContextTypes

class BaseCommand(ABC):
    """Base class for all bot commands"""
    
    def __init__(self):
        self.name = self.__class__.__name__.lower().replace("command", "")
    
    @abstractmethod
    async def execute(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> Any:
        """Execute the command"""
        pass
    
    async def check_permission(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """Check if user has permission"""
        return True
    
    async def validate_args(self, args: list) -> bool:
        """Validate command arguments"""
        return True
    
    async def on_error(self, update: Update, context: ContextTypes.DEFAULT_TYPE, error: Exception):
        """Handle command errors"""
        await update.message.reply_text(
            f"❌ An error occurred: {str(error)}"
        )