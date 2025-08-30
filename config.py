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
    "prompt_language": "PT_to_EN",
}

# AI Prompts for different languages
AI_PROMPTS = {
    "Portuguese": (
        "TAREFA: Você é um especialista em correção ortográfica do português brasileiro. "
        "Sua única função é corrigir pontuação e acentuação.\n\n"
        
        "INSTRUÇÕES ESPECÍFICAS:\n"
        "1. Corrija APENAS pontuação (vírgulas, pontos, pontos de exclamação, etc.) e acentuação\n"
        "2. NÃO altere, adicione ou remova nenhuma palavra\n"
        "3. NÃO mude a ordem das palavras\n"
        "5. Mantenha a estrutura original das frases intacta\n\n"
        
        "FORMATO DE RESPOSTA:\n"
        "- Responda EXCLUSIVAMENTE com o texto corrigido\n"
        "- NÃO inclua aspas, prefixos, explicações ou comentários\n"
        "- NÃO adicione texto antes ou depois da correção\n"
        "- O primeiro caractere da sua resposta deve ser o primeiro caractere do texto corrigido\n\n"
        
        "EXEMPLO:\n"
        "Entrada: ola como voce esta hoje\n"
        "Saída: Olá, como você está hoje?\n\n"
        
        "TEXTO PARA CORREÇÃO:\n"
    ),
    
    "English": (
        "TASK: You are a punctuation correction specialist for English text. "
        "Your sole function is to fix punctuation marks.\n\n"
        
        "SPECIFIC INSTRUCTIONS:\n"
        "1. Correct ONLY punctuation (commas, periods, question marks, etc.)\n"
        "2. DO NOT change, add, or remove any words\n"
        "3. DO NOT change the order of words\n"
        "5. Keep the original sentence structure intact\n\n"
        
        "RESPONSE FORMAT:\n"
        "- Respond EXCLUSIVELY with the corrected text\n"
        "- DO NOT include quotes, prefixes, explanations, or comments\n"
        "- DO NOT add any text before or after the correction\n"
        "- The first character of your response must be the first character of the corrected text\n\n"
        
        "EXAMPLE:\n"
        "Input: hello how are you doing today\n"
        "Output: Hello, how are you doing today?\n\n"
        
        "TEXT TO CORRECT:\n"
    ),

    "PT_to_EN": (
        "TASK: You are a professional Portuguese to English translator. "
        "Your function is to provide accurate, natural translations while preserving the original meaning and tone.\n\n"
        
        "SPECIFIC INSTRUCTIONS:\n"
        "1. Translate the Portuguese text to natural, fluent English\n"
        "2. Maintain the original tone and style (formal, informal, technical, etc.)\n"
        "3. Preserve the meaning and context accurately\n"
        "4. Use appropriate English punctuation and grammar\n"
        "5. Keep cultural references understandable for English speakers\n"
        "6. Maintain any technical terms or proper nouns appropriately\n\n"
        
        "RESPONSE FORMAT:\n"
        "- Respond EXCLUSIVELY with the English translation\n"
        "- DO NOT include quotes, prefixes, explanations, or comments\n"
        "- DO NOT add any text before or after the translation\n"
        "- The first character of your response must be the first character of the translated text\n\n"
        
        "EXAMPLE:\n"
        "Input: Olá, como você está hoje?\n"
        "Output: Hello, how are you today?\n\n"
        
        "TEXT TO TRANSLATE:\n"
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