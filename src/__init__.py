"""
Telegram Bot - Main Package
A professional Telegram bot for video streaming and management
"""

__version__ = "1.0.0"
__author__ = "NOSTRA"

from .config import Config
from .bot import main

__all__ = ["Config", "main"]