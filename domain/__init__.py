"""
Domain Layer
============
Core business logic and domain models
"""

from .models import AppSettings, CorrectionRequest, CorrectionResult
from .services import TextCorrectionService

__all__ = [
    'AppSettings',
    'CorrectionRequest', 
    'CorrectionResult',
    'TextCorrectionService'
]