"""
Configuration file for Text Correction Tool
===========================================
Centralized configuration and constants
"""

# API Keys and External Services
GEMINI_API_KEY = "your_gemini_api_key_here"

# Application Constants
APP_NAME = "Text Correction Tool"
APP_VERSION = "2.0.0"
APP_DESCRIPTION = "AI-powered text correction with global hotkey support"

# File Paths
LOG_FILE = "text_correction.log"
SETTINGS_FILE = "settings.json"

# Default Application Settings
DEFAULT_SETTINGS = {
    "hotkey": "alt+s",
    "auto_paste": True,
    "show_notifications": True,
    "prompt_language": "Portuguese",
}

# AI Prompts for different languages
AI_PROMPTS = {
    "Portuguese": (
        "Corrija a pontuação do texto a seguir, aplicando toda a pontuação "
        "corretamente sem alterar nenhuma palavra. Mantenha a capitalização "
        "apenas onde já existe. Texto:\n\n"
    ),
    "English": (
        "Fix the punctuation in the following text, placing all punctuation correctly "
        "without changing any words. Maintain capitalization only where it already exists. "
        "Text:\n\n"
    ),
}

# UI Configuration
NOTIFICATION_COLORS = {
    "info": "#0078d4",
    "success": "#107c10", 
    "warning": "#ff8c00",
    "error": "#d13438"
}

NOTIFICATION_DURATION = 4000  # milliseconds
NOTIFICATION_POSITION = {
    "width": 350,
    "height": 120,
    "margin_x": 20,
    "margin_y": 40
}

# System Tray Icon Configuration
TRAY_ICON_SIZE = (64, 64)
TRAY_ICON_BACKGROUND_COLOR = (0, 120, 212)
TRAY_ICON_TEXT = "TC"
TRAY_ICON_TEXT_COLOR = (255, 255, 255)

# Logging Configuration
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_LEVEL = "INFO"