"""
Configuration management for the bot
"""

import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

@dataclass
class Config:
    """Application configuration"""
    
    # Telegram
    TELEGRAM_TOKEN: str
    BOT_VERSION: str
    
    # Supabase
    SUPABASE_URL: str
    SUPABASE_KEY: str
    
    # Owner
    OWNER_USERNAME: str
    OWNER_ID: int
    
    # Environment
    ENVIRONMENT: str
    LOG_LEVEL: str
    PORT: int
    
    # Security
    SECRET_KEY: str
    SESSION_TIMEOUT: int
    
    # Rate Limiting
    MAX_REQUESTS_PER_MINUTE: int
    ADMIN_MAX_REQUESTS: int
    
    # File Limits
    MAX_VIDEO_SIZE_MB: int
    MAX_VIDEO_DURATION_SECONDS: int
    
    # Redis
    REDIS_URL: Optional[str] = None
    
    def __init__(self):
        """Load configuration from environment"""
        load_dotenv("bot.env")
        
        self.TELEGRAM_TOKEN = self._get_env("TELEGRAM_TOKEN")
        self.BOT_VERSION = self._get_env("BOT_VERSION", "1.0.0")
        
        self.SUPABASE_URL = self._get_env("SUPABASE_URL")
        self.SUPABASE_KEY = self._get_env("SUPABASE_KEY")
        
        self.OWNER_USERNAME = self._get_env("OWNER_USERNAME")
        self.OWNER_ID = int(self._get_env("OWNER_ID", "0"))
        
        self.ENVIRONMENT = self._get_env("ENVIRONMENT", "development")
        self.LOG_LEVEL = self._get_env("LOG_LEVEL", "INFO")
        self.PORT = int(self._get_env("PORT", "8080"))
        
        self.SECRET_KEY = self._get_env("SECRET_KEY", "default-secret-key-change-me")
        self.SESSION_TIMEOUT = int(self._get_env("SESSION_TIMEOUT", "3600"))
        
        self.MAX_REQUESTS_PER_MINUTE = int(self._get_env("MAX_REQUESTS_PER_MINUTE", "30"))
        self.ADMIN_MAX_REQUESTS = int(self._get_env("ADMIN_MAX_REQUESTS", "60"))
        
        self.MAX_VIDEO_SIZE_MB = int(self._get_env("MAX_VIDEO_SIZE_MB", "50"))
        self.MAX_VIDEO_DURATION_SECONDS = int(self._get_env("MAX_VIDEO_DURATION_SECONDS", "3600"))
        
        self.REDIS_URL = self._get_env("REDIS_URL", None)
    
    def _get_env(self, key: str, default: Optional[str] = None) -> str:
        """Get environment variable or raise error"""
        value = os.getenv(key, default)
        if value is None:
            raise ValueError(f"Missing required environment variable: {key}")
        return value
    
    @property
    def is_production(self) -> bool:
        """Check if running in production"""
        return self.ENVIRONMENT.lower() == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development"""
        return self.ENVIRONMENT.lower() == "development"
