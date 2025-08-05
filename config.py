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
        "Corrija apenas a pontuação e acentuação do texto a seguir. "
        "Mantenha todas as palavras exatamente como estão, apenas "
        "adicione ou corrija a pontuação necessária. "
        "Responda APENAS com o texto corrigido, sem aspas ou prefixos.\n\n"
        "Texto para correção:\n"
    ),
    "English": (
        "Fix only the punctuation in the following text. "
        "Keep all words exactly as they are, only add or correct "
        "the necessary punctuation. "
        "Respond ONLY with the corrected text, without quotes or prefixes.\n\n"
        "Text to correct:\n"
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