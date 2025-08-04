"""
Text Correction Tool - Main Application
=======================================
AI-powered text correction with global hotkey support

This is the main entry point and composition root for the application.
It assembles all components and manages the application lifecycle.

Author: [Your Name]
Version: 2.0.0
License: MIT
"""

import asyncio
import logging
import sys
import threading
import tkinter as tk
from tkinter import messagebox
from typing import Optional

# Import configuration
from config import APP_NAME, APP_VERSION, GEMINI_API_KEY, LOG_FILE

# Import domain layer
from domain.models import AppSettings
from domain.services import TextCorrectionService

# Import application layer
from application.use_cases import TextCorrectionUseCase, SettingsUseCase

# Import infrastructure layer
from infrastructure.ai_providers import GeminiAIProvider
from infrastructure.repositories import SettingsRepository
from infrastructure.services import LoggingService, ClipboardService

# Import presentation layer
from presentation.ui_components import NotificationService, SettingsWindow, AboutDialog
from presentation.system_integration import SystemTrayManager, HotkeyListener, WindowManager


class TextCorrectionApp:
    """
    Main application class - Composition Root.
    
    This class serves as the application's composition root, responsible for:
    - Dependency injection and service wiring
    - Application lifecycle management
    - Error handling and logging
    - Component initialization and cleanup
    """
    
    def __init__(self):
        """Initialize the application and all its components."""
        # Setup logging first
        LoggingService.setup(APP_NAME, LOG_FILE)
        self.logger = logging.getLogger(APP_NAME)
        
        # Initialize state
        self._is_running = False
        self._shutdown_requested = False
        
        # Initialize components
        self._initialize_repositories()
        self._initialize_infrastructure_services()
        self._initialize_domain_services()
        self._initialize_application_services()
        self._initialize_presentation_layer()
        
        self.logger.info(f"Application initialized - {APP_NAME} v{APP_VERSION}")
    
    def _initialize_repositories(self) -> None:
        """Initialize data repositories."""
        try:
            self.settings_repository = SettingsRepository()
            self.current_settings = self.settings_repository.load()
            
            self.logger.info("Repositories initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize repositories: {e}")
            raise
    
    def _initialize_infrastructure_services(self) -> None:
        """Initialize infrastructure services."""
        try:
            # AI Provider
            if not GEMINI_API_KEY:
                raise ValueError("GEMINI_API_KEY not configured in config.py")
            
            self.ai_provider = GeminiAIProvider(GEMINI_API_KEY)
            
            # Clipboard Service
            self.clipboard_service = ClipboardService()
            
            self.logger.info("Infrastructure services initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize infrastructure services: {e}")
            raise
    
    def _initialize_domain_services(self) -> None:
        """Initialize domain services."""
        try:
            self.text_correction_service = TextCorrectionService(self.ai_provider)
            
            self.logger.info("Domain services initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize domain services: {e}")
            raise
    
    def _initialize_application_services(self) -> None:
        """Initialize application services (use cases)."""
        try:
            # Will be initialized after UI components
            self.text_correction_use_case = None
            self.settings_use_case = None
            
        except Exception as e:
            self.logger.error(f"Failed to initialize application services: {e}")
            raise
    
    def _initialize_presentation_layer(self) -> None:
        """Initialize presentation layer components."""
        try:
            # Initialize main window (hidden)
            self.root = tk.Tk()
            self.root.withdraw()  # Hide main window
            self.root.title(APP_NAME)
            
            # Window manager
            self.window_manager = WindowManager()
            self.window_manager.register_window("main", self.root)
            
            # Notification service
            self.notification_service = NotificationService(self.root)
            
            # Now initialize application services with UI dependencies
            self.text_correction_use_case = TextCorrectionUseCase(
                self.text_correction_service,
                self.clipboard_service,
                self.notification_service
            )
            
            self.settings_use_case = SettingsUseCase(
                self.settings_repository,
                self.notification_service
            )
            
            # System tray manager
            self.system_tray = SystemTrayManager(
                APP_NAME,
                self._show_settings_window,
                self._show_about_dialog,
                self._request_shutdown
            )
            
            # Hotkey listener (will be started later)
            self.hotkey_listener = None
            self._setup_hotkey_listener()
            
            self.logger.info("Presentation layer initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize presentation layer: {e}")
            raise
    
    def _setup_hotkey_listener(self) -> None:
        """Setup global hotkey listener."""
        try:
            def hotkey_callback():
                """Callback for hotkey activation."""
                # Run correction use case in async context
                def run_correction():
                    try:
                        asyncio.run(
                            self.text_correction_use_case.execute(self.current_settings)
                        )
                    except Exception as e:
                        self.logger.error(f"Error in hotkey callback: {e}")
                
                # Execute in separate thread to avoid blocking
                threading.Thread(target=run_correction, daemon=True).start()
            
            self.hotkey_listener = HotkeyListener(
                self.current_settings.hotkey,
                hotkey_callback
            )
            
            self.logger.info(f"Hotkey listener configured for: {self.current_settings.hotkey}")
            
        except Exception as e:
            self.logger.error(f"Failed to setup hotkey listener: {e}")
            raise
    
    def _show_settings_window(self) -> None:
        """Show settings configuration window."""
        try:
            def on_settings_saved(new_settings: AppSettings):
                """Handle settings save."""
                self.current_settings = new_settings
                success = self.settings_use_case.save_settings(new_settings)
                
                if success:
                    # Note: Hotkey changes require restart
                    self.logger.info("Settings updated successfully")
            
            settings_window = SettingsWindow(
                self.root,
                self.current_settings,
                on_settings_saved
            )
            settings_window.show()
            
        except Exception as e:
            self.logger.error(f"Error showing settings window: {e}")
            self.notification_service.show_error(f"Failed to open settings: {str(e)}")
    
    def _show_about_dialog(self) -> None:
        """Show about dialog."""
        try:
            about_dialog = AboutDialog(self.root, APP_NAME, APP_VERSION)
            about_dialog.show()
        except Exception as e:
            self.logger.error(f"Error showing about dialog: {e}")
    
    def _request_shutdown(self) -> None:
        """Request application shutdown."""
        self.logger.info("Shutdown requested by user")
        self._shutdown_requested = True
        self._shutdown()
    
    def _shutdown(self) -> None:
        """Shutdown the application gracefully."""
        try:
            self.logger.info("Starting application shutdown...")
            
            # Stop hotkey listener
            if self.hotkey_listener and self.hotkey_listener.is_running:
                self.hotkey_listener.stop()
            
            # Stop system tray
            if self.system_tray and self.system_tray.is_running:
                self.system_tray.stop()
            
            # Close all windows
            if hasattr(self, 'window_manager'):
                self.window_manager.close_all_windows()
            
            # Clear notifications
            if hasattr(self, 'notification_service'):
                self.notification_service.clear_all_notifications()
            
            # Quit main loop
            if self.root:
                self.root.quit()
            
            self._is_running = False
            self.logger.info("Application shutdown completed")
            
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")
    
    def _start_background_services(self) -> None:
        """Start background services in separate threads."""
        try:
            # Start hotkey listener
            if self.hotkey_listener:
                hotkey_thread = threading.Thread(
                    target=self.hotkey_listener.start,
                    name="HotkeyListener",
                    daemon=True
                )
                hotkey_thread.start()
                self.logger.info("Hotkey listener thread started")
            
            # Start system tray
            self.system_tray.setup()
            self.logger.info("System tray initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to start background services: {e}")
            raise
    
    def _show_startup_notification(self) -> None:
        """Show startup notification to user."""
        try:
            message = (
                f"Application started successfully!\n"
                f"Use {self.current_settings.hotkey} to correct text from clipboard."
            )
            
            self.notification_service.show_success(message, duration=5000)
            
        except Exception as e:
            self.logger.error(f"Error showing startup notification: {e}")
    
    def _perform_health_checks(self) -> bool:
        """
        Perform application health checks.
        
        Returns:
            True if all checks pass, False otherwise
        """
        try:
            self.logger.info("Performing application health checks...")
            
            # Check AI provider
            # Note: We'll skip the health check to avoid API calls during startup
            # In production, you might want to implement this as an optional check
            
            # Check clipboard access
            clipboard_info = self.clipboard_service.get_clipboard_info()
            if "error" in clipboard_info:
                self.logger.warning(f"Clipboard access issue: {clipboard_info['error']}")
            
            # Check hotkey format
            if self.hotkey_listener and not self.hotkey_listener.test_hotkey_format():
                self.logger.error(f"Invalid hotkey format: {self.current_settings.hotkey}")
                return False
            
            self.logger.info("Health checks completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return False
    
    def run(self) -> None:
        """
        Run the application.
        
        This is the main entry point that starts all services and begins
        the application's main event loop.
        """
        try:
            self.logger.info(f"Starting {APP_NAME} v{APP_VERSION}")
            
            # Perform health checks
            if not self._perform_health_checks():
                self.logger.error("Health checks failed - aborting startup")
                messagebox.showerror(
                    "Startup Error",
                    "Application health checks failed. Please check the configuration."
                )
                return
            
            # Start background services
            self._start_background_services()
            
            # Show startup notification
            self._show_startup_notification()
            
            # Start UI queue processing
            self.notification_service.process_queue()
            
            # Set running flag
            self._is_running = True
            
            # Start main event loop
            self.logger.info("Starting main event loop")
            self.root.mainloop()
            
            self.logger.info("Main event loop ended")
            
        except KeyboardInterrupt:
            self.logger.info("Application interrupted by user (Ctrl+C)")
        except Exception as e:
            error_msg = f"Critical application error: {str(e)}"
            self.logger.critical(error_msg)
            
            # Show error dialog if possible
            try:
                messagebox.showerror("Critical Error", error_msg)
            except:
                pass
                
        finally:
            # Ensure cleanup happens
            if not self._shutdown_requested:
                self._shutdown()
    
    @property
    def is_running(self) -> bool:
        """Check if application is currently running."""
        return self._is_running
    
    def get_status_info(self) -> dict:
        """
        Get application status information.
        
        Returns:
            Dictionary with current application status
        """
        return {
            "app_name": APP_NAME,
            "version": APP_VERSION,
            "is_running": self.is_running,
            "current_hotkey": self.current_settings.hotkey if self.current_settings else "unknown",
            "hotkey_listener_running": self.hotkey_listener.is_running if self.hotkey_listener else False,
            "system_tray_running": self.system_tray.is_running if self.system_tray else False,
            "active_windows": self.window_manager.get_window_count() if hasattr(self, 'window_manager') else 0
        }


def main():
    """
    Application entry point.
    
    This function creates and runs the main application instance.
    It handles top-level exception catching and logging.
    """
    app = None
    
    try:
        # Create application instance
        app = TextCorrectionApp()
        
        # Run the application
        app.run()
        
    except Exception as e:
        # Top-level exception handler
        error_msg = f"Fatal application error: {str(e)}"
        
        # Try to log the error
        try:
            if app and hasattr(app, 'logger'):
                app.logger.critical(error_msg)
            else:
                print(f"CRITICAL: {error_msg}", file=sys.stderr)
        except:
            print(f"CRITICAL: {error_msg}", file=sys.stderr)
        
        # Show error dialog if possible
        try:
            import tkinter as tk
            from tkinter import messagebox
            
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Fatal Error", error_msg)
            root.destroy()
            
        except:
            pass
        
        # Exit with error code
        sys.exit(1)
    
    except KeyboardInterrupt:
        print("\nApplication interrupted by user", file=sys.stderr)
        sys.exit(0)


if __name__ == "__main__":
    main()