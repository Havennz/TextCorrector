"""
Domain Models
=================================
Core business entities and value objects with robust validation
"""

from dataclasses import dataclass
from typing import Optional, Any


@dataclass
class CorrectionRequest:
    """Domain model representing a text correction request."""
    original_text: str
    language: str
    auto_paste: bool = True
    show_notification: bool = True
    
    def __post_init__(self):
        """Validate and clean request data after initialization."""
        # Handle None values
        if self.original_text is None:
            self.original_text = ""
        
        # Convert to string if not already
        if not isinstance(self.original_text, str):
            self.original_text = str(self.original_text)
        
        if not isinstance(self.language, str):
            raise ValueError("language must be a string")
        
        if self.language not in ["Portuguese", "English"]:
            raise ValueError("language must be 'Portuguese' or 'English'")
    
    @classmethod
    def create_safe(cls, original_text: Any, language: str, **kwargs) -> 'CorrectionRequest':
        """
        Create a CorrectionRequest with safe handling of input types.
        
        Args:
            original_text: Text to correct (any type, will be converted to string)
            language: Language for correction
            **kwargs: Additional parameters
            
        Returns:
            CorrectionRequest instance
        """
        # Safe conversion to string
        if original_text is None:
            text = ""
        elif isinstance(original_text, (bytes, bytearray)):
            try:
                text = original_text.decode('utf-8', errors='replace')
            except:
                text = str(original_text)
        else:
            text = str(original_text)
        
        return cls(
            original_text=text,
            language=language,
            **kwargs
        )


@dataclass
class CorrectionResult:
    """Domain model representing the result of a text correction operation."""
    original_text: str
    corrected_text: str
    success: bool
    error_message: Optional[str] = None
    processing_time: float = 0.0
    
    @property
    def has_changes(self) -> bool:
        """Check if the correction resulted in any changes."""
        return self.original_text.strip() != self.corrected_text.strip()
    
    @property
    def is_valid(self) -> bool:
        """Check if the result is valid."""
        return self.success and bool(self.corrected_text.strip())


@dataclass
class AppSettings:
    """Domain model representing application settings."""
    hotkey: str = "alt+s"
    auto_paste: bool = True
    show_notifications: bool = True
    prompt_language: str = "Portuguese"
    
    def __post_init__(self):
        """Validate settings after initialization."""
        if not isinstance(self.hotkey, str) or not self.hotkey.strip():
            raise ValueError("hotkey must be a non-empty string")
        
        if self.prompt_language not in ["Portuguese", "English"]:
            raise ValueError("prompt_language must be 'Portuguese' or 'English'")
    
    @property
    def normalized_hotkey(self) -> str:
        """Get normalized hotkey format."""
        return self.hotkey.lower().strip()
    
    def to_dict(self) -> dict:
        """Convert settings to dictionary."""
        return {
            "hotkey": self.hotkey,
            "auto_paste": self.auto_paste,
            "show_notifications": self.show_notifications,
            "prompt_language": self.prompt_language
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'AppSettings':
        """Create settings from dictionary."""
        return cls(
            hotkey=data.get("hotkey", "alt+s"),
            auto_paste=data.get("auto_paste", True),
            show_notifications=data.get("show_notifications", True),
            prompt_language=data.get("prompt_language", "Portuguese")
        )


# =============================================================================
# CORREÇÃO 3: application/use_cases.py - Uso do método seguro
# =============================================================================

"""
Application Use Cases - VERSÃO CORRIGIDA
========================================
Orchestrates business logic with robust error handling
"""

import asyncio
import logging
from typing import Protocol

from domain.models import AppSettings, CorrectionRequest
from domain.services import TextCorrectionService


class ClipboardService(Protocol):
    """Protocol for clipboard operations."""
    
    def get_text(self) -> str:
        """Get text from clipboard."""
        ...
    
    def set_text(self, text: str) -> None:
        """Set text to clipboard."""
        ...
    
    async def paste(self) -> None:
        """Simulate paste operation."""
        ...


class NotificationService(Protocol):
    """Protocol for desktop notification services."""
    
    def show_info(self, message: str) -> None:
        """Show information notification."""
        ...
    
    def show_success(self, message: str) -> None:
        """Show success notification."""
        ...
    
    def show_warning(self, message: str) -> None:
        """Show warning notification."""
        ...
    
    def show_error(self, message: str) -> None:
        """Show error notification."""
        ...


class TextCorrectionUseCase:
    """Use case for handling the complete text correction workflow."""
    
    def __init__(
        self,
        correction_service: TextCorrectionService,
        clipboard_service: ClipboardService,
        notification_service: NotificationService
    ):
        """Initialize the use case with required services."""
        self.correction_service = correction_service
        self.clipboard_service = clipboard_service
        self.notification_service = notification_service
        self.logger = logging.getLogger("TextCorrectionUseCase")
    
    async def execute(self, settings: AppSettings) -> None:
        """Execute the complete text correction workflow with robust error handling."""
        try:
            # Step 1: Get text from clipboard with robust handling
            original_text = self.clipboard_service.get_text()
            
            # Handle various clipboard content types
            if original_text is None:
                original_text = ""
            
            if not isinstance(original_text, str):
                # Try to convert to string safely
                try:
                    original_text = str(original_text)
                except Exception as e:
                    self.logger.error(f"Failed to convert clipboard content to string: {e}")
                    original_text = ""
            
            if not original_text.strip():
                self.logger.warning("Attempted correction with empty or invalid clipboard content")
                if settings.show_notifications:
                    self.notification_service.show_warning(
                        "Clipboard is empty or contains invalid content. Copy some text first!"
                    )
                return
            
            # Step 2: Show processing notification
            if settings.show_notifications:
                self.notification_service.show_info(
                    "Processing text correction..."
                )
            
            # Step 3: Create correction request using safe method
            request = CorrectionRequest.create_safe(
                original_text=original_text,
                language=settings.prompt_language,
                auto_paste=settings.auto_paste,
                show_notification=settings.show_notifications
            )
            
            # Validate request
            is_valid, error_message = self.correction_service.validate_request(request)
            if not is_valid:
                self.logger.error(f"Invalid correction request: {error_message}")
                if settings.show_notifications:
                    self.notification_service.show_error(f"Validation error: {error_message}")
                return
            
            # Step 4: Process text correction
            self.logger.info("Starting text correction process")
            result = await self.correction_service.correct_text(request)
            
            if not result.success:
                self.logger.error(f"Text correction failed: {result.error_message}")
                if settings.show_notifications:
                    self.notification_service.show_error(
                        f"Correction failed: {result.error_message}"
                    )
                return
            
            # Step 5: Update clipboard with corrected text
            self.clipboard_service.set_text(result.corrected_text)
            self.logger.info("Corrected text copied to clipboard")
            
            # Step 6: Auto-paste if enabled
            if settings.auto_paste:
                await asyncio.sleep(0.1)  # Brief delay for stability
                await self.clipboard_service.paste()
                self.logger.info("Auto-paste completed")
            
            # Step 7: Show success notification
            if settings.show_notifications:
                self._show_success_notification(result, settings.auto_paste)
            
            self.logger.info(
                f"Text correction workflow completed successfully in {result.processing_time:.2f}s"
            )
            
        except Exception as e:
            error_msg = f"Unexpected error in text correction workflow: {str(e)}"
            self.logger.error(error_msg)
            
            if settings.show_notifications:
                self.notification_service.show_error(
                    f"Unexpected error: {str(e)}"
                )
    
    def _show_success_notification(self, result, auto_paste_enabled: bool) -> None:
        """Show success notification with appropriate message."""
        # Create preview of corrected text
        preview = self._create_text_preview(result.corrected_text)
        
        # Determine message based on whether changes were made
        if result.has_changes:
            action = "pasted" if auto_paste_enabled else "copied to clipboard"
            message = f"Text corrected and {action}!\n\nPreview: {preview}"
        else:
            action = "pasted" if auto_paste_enabled else "copied to clipboard"
            message = f"No changes needed. Text {action}.\n\nPreview: {preview}"
        
        self.notification_service.show_success(message)
    
    def _create_text_preview(self, text: str, max_length: int = 80) -> str:
        """Create a preview of the text for notifications."""
        if len(text) <= max_length:
            return text
        
        return f"{text[:max_length - 3]}..."


class SettingsUseCase:
    """Use case for managing application settings."""
    
    def __init__(self, settings_repository, notification_service: NotificationService):
        """Initialize settings use case."""
        self.settings_repository = settings_repository
        self.notification_service = notification_service
        self.logger = logging.getLogger("SettingsUseCase")
    
    def load_settings(self) -> AppSettings:
        """Load application settings."""
        try:
            settings = self.settings_repository.load()
            self.logger.info("Settings loaded successfully")
            return settings
        except Exception as e:
            self.logger.error(f"Failed to load settings: {e}")
            # Return default settings on error
            return AppSettings()
    
    def save_settings(self, settings: AppSettings) -> bool:
        """Save application settings."""
        try:
            self.settings_repository.save(settings)
            self.logger.info("Settings saved successfully")
            
            self.notification_service.show_success(
                "Settings saved successfully!\nRestart the application to apply hotkey changes."
            )
            return True
            
        except Exception as e:
            error_msg = f"Failed to save settings: {str(e)}"
            self.logger.error(error_msg)
            self.notification_service.show_error(error_msg)
            return False