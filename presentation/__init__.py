"""
Presentation Layer
==================
User interface components and system integration
"""

from .ui_components import NotificationService, SettingsWindow, AboutDialog
from .system_integration import SystemTrayManager, HotkeyListener, WindowManager

__all__ = [
    'NotificationService',
    'SettingsWindow',
    'AboutDialog',
    'SystemTrayManager',
    'HotkeyListener',
    'WindowManager'
]