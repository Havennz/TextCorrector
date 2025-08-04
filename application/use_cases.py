"""
Application Use Cases
====================
Orchestrates business logic and coordinates between layers
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
    """
    Use case for handling the complete text correction workflow.
    
    This class orchestrates the entire text correction process:
    1. Gets text from clipboard
    2. Validates the text
    3. Processes correction via domain service
    4. Updates clipboard with result
    5. Handles auto-paste if enabled
    6. Shows appropriate notifications
    """
    
    def __init__(
        self,
        correction_service: TextCorrectionService,
        clipboard_service: ClipboardService,
        notification_service: NotificationService
    ):
        """
        Initialize the use case with required services.
        
        Args:
            correction_service: Domain service for text correction
            clipboard_service: Service for clipboard operations  
            notification_service: Service for desktop notifications
        """
        self.correction_service = correction_service
        self.clipboard_service = clipboard_service
        self.notification_service = notification_service
        self.logger = logging.getLogger("TextCorrectionUseCase")
    
    async def execute(self, settings: AppSettings) -> None:
        """
        Execute the complete text correction workflow.
        
        Args:
            settings: Current application settings
        """
        try:
            # Step 1: Get text from clipboard
            original_text = self.clipboard_service.get_text()
            
            if not original_text.strip():
                self.logger.warning("Attempted correction with empty clipboard")
                if settings.show_notifications:
                    self.notification_service.show_warning(
                        "Clipboard is empty. Copy some text first!"
                    )
                return
            
            # Step 2: Show processing notification
            if settings.show_notifications:
                self.notification_service.show_info(
                    "Processing text correction..."
                )
            
            # Step 3: Create and validate correction request
            request = CorrectionRequest(
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
        """
        Show success notification with appropriate message.
        
        Args:
            result: The correction result
            auto_paste_enabled: Whether auto-paste is enabled
        """
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
        """
        Create a preview of the text for notifications.
        
        Args:
            text: The text to preview
            max_length: Maximum length of the preview
            
        Returns:
            Truncated text with ellipsis if needed
        """
        if len(text) <= max_length:
            return text
        
        return f"{text[:max_length - 3]}..."


class SettingsUseCase:
    """
    Use case for managing application settings.
    """
    
    def __init__(self, settings_repository, notification_service: NotificationService):
        """
        Initialize settings use case.
        
        Args:
            settings_repository: Repository for settings persistence
            notification_service: Service for notifications
        """
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
        """
        Save application settings.
        
        Args:
            settings: Settings to save
            
        Returns:
            True if saved successfully, False otherwise
        """
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