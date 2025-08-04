"""
UI Components
=============
User interface components and notification management
"""

import logging
import queue
import tkinter as tk
from tkinter import messagebox, ttk, BooleanVar, StringVar
from typing import Callable, Optional

from domain.models import AppSettings
from config import NOTIFICATION_COLORS, NOTIFICATION_DURATION, NOTIFICATION_POSITION


class NotificationService:
    """
    Service for managing desktop notifications.
    
    Provides a clean interface for showing different types of notifications
    with consistent styling and behavior.
    """
    
    def __init__(self, root: tk.Tk):
        """
        Initialize notification service.
        
        Args:
            root: Main Tkinter root window
        """
        self.root = root
        self.ui_queue = queue.Queue()
        self.logger = logging.getLogger("NotificationService")
        self.active_notifications = []
    
    def show_info(self, message: str, duration: int = NOTIFICATION_DURATION) -> None:
        """Show information notification."""
        self._queue_notification("Info", message, NOTIFICATION_COLORS["info"], duration)
    
    def show_success(self, message: str, duration: int = NOTIFICATION_DURATION) -> None:
        """Show success notification."""
        self._queue_notification("Success", message, NOTIFICATION_COLORS["success"], duration)
    
    def show_warning(self, message: str, duration: int = NOTIFICATION_DURATION) -> None:
        """Show warning notification."""
        self._queue_notification("Warning", message, NOTIFICATION_COLORS["warning"], duration)
    
    def show_error(self, message: str, duration: int = NOTIFICATION_DURATION) -> None:
        """Show error notification."""
        self._queue_notification("Error", message, NOTIFICATION_COLORS["error"], duration)
    
    def _queue_notification(self, title: str, message: str, color: str, duration: int) -> None:
        """Queue notification for display in main thread."""
        self.ui_queue.put(("notification", title, message, color, duration))
    
    def _create_notification_window(self, title: str, message: str, color: str, duration: int) -> None:
        """Create and display notification window."""
        try:
            window = tk.Toplevel(self.root)
            window.overrideredirect(True)
            window.attributes("-topmost", True)
            
            # Calculate position
            screen_width = window.winfo_screenwidth()
            screen_height = window.winfo_screenheight()
            
            w_width = NOTIFICATION_POSITION["width"]
            w_height = NOTIFICATION_POSITION["height"]
            margin_x = NOTIFICATION_POSITION["margin_x"]
            margin_y = NOTIFICATION_POSITION["margin_y"]
            
            # Stack notifications vertically if multiple are active
            y_offset = len(self.active_notifications) * (w_height + 10)
            
            x_pos = screen_width - w_width - margin_x
            y_pos = screen_height - w_height - margin_y - y_offset
            
            window.geometry(f"{w_width}x{w_height}+{x_pos}+{y_pos}")
            window.configure(bg="#2e2e2e")
            
            # Add to active notifications
            self.active_notifications.append(window)
            
            # Create content
            self._create_notification_content(window, title, message, color)
            
            # Schedule destruction
            def destroy_notification():
                try:
                    if window in self.active_notifications:
                        self.active_notifications.remove(window)
                    window.destroy()
                except:
                    pass
            
            window.after(duration, destroy_notification)
            
            # Add click to close functionality
            def on_click(event=None):
                destroy_notification()
            
            window.bind("<Button-1>", on_click)
            for child in window.winfo_children():
                child.bind("<Button-1>", on_click)
            
        except Exception as e:
            self.logger.error(f"Error creating notification: {e}")
    
    def _create_notification_content(self, window: tk.Toplevel, title: str, message: str, color: str) -> None:
        """Create notification window content."""
        # Color border at top
        border_frame = tk.Frame(window, bg=color, height=4)
        border_frame.pack(fill=tk.X)
        
        # Main content frame
        content_frame = tk.Frame(window, bg="#2e2e2e", padx=15, pady=12)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = tk.Label(
            content_frame,
            text=title,
            fg="white",
            bg="#2e2e2e",
            font=("Segoe UI", 11, "bold"),
            anchor="w"
        )
        title_label.pack(fill=tk.X)
        
        # Message
        message_display = self._format_message(message)
        message_label = tk.Label(
            content_frame,
            text=message_display,
            fg="#cccccc",
            bg="#2e2e2e",
            font=("Segoe UI", 9),
            wraplength=320,
            justify=tk.LEFT,
            anchor="w"
        )
        message_label.pack(fill=tk.X, pady=(5, 0))
        
        # Close indicator
        close_label = tk.Label(
            content_frame,
            text="× Click to close",
            fg="#888888",
            bg="#2e2e2e",
            font=("Segoe UI", 8),
            anchor="e"
        )
        close_label.pack(fill=tk.X, pady=(5, 0))
    
    def _format_message(self, message: str, max_length: int = 150) -> str:
        """Format message for display."""
        if len(message) <= max_length:
            return message
        return f"{message[:max_length-3]}..."
    
    def process_queue(self) -> None:
        """Process notification queue in main thread."""
        try:
            while True:
                item = self.ui_queue.get_nowait()
                if item[0] == "notification":
                    _, title, message, color, duration = item
                    self._create_notification_window(title, message, color, duration)
                else:
                    self.logger.warning(f"Unknown UI queue item: {item}")
        except queue.Empty:
            pass
        
        # Schedule next queue processing
        self.root.after(100, self.process_queue)
    
    def clear_all_notifications(self) -> None:
        """Clear all active notifications."""
        for window in self.active_notifications[:]:
            try:
                window.destroy()
            except:
                pass
        self.active_notifications.clear()


class SettingsWindow:
    """
    Settings configuration window.
    
    Provides a user-friendly interface for configuring application settings.
    """
    
    def __init__(
        self,
        parent: tk.Tk,
        current_settings: AppSettings,
        on_save_callback: Callable[[AppSettings], None]
    ):
        """
        Initialize settings window.
        
        Args:
            parent: Parent window
            current_settings: Current application settings
            on_save_callback: Callback function when settings are saved
        """
        self.parent = parent
        self.current_settings = current_settings
        self.on_save_callback = on_save_callback
        self.logger = logging.getLogger("SettingsWindow")
        
        # Variables for form fields
        self.hotkey_var = StringVar(value=current_settings.hotkey)
        self.auto_paste_var = BooleanVar(value=current_settings.auto_paste)
        self.notifications_var = BooleanVar(value=current_settings.show_notifications)
        self.language_var = StringVar(value=current_settings.prompt_language)
        
        self.window: Optional[tk.Toplevel] = None
    
    def show(self) -> None:
        """Display the settings window."""
        try:
            self.window = tk.Toplevel(self.parent)
            self.window.title("Text Correction - Settings")
            self.window.geometry("520x450")
            self.window.resizable(False, False)
            self.window.grab_set()  # Make modal
            
            # Center window on screen
            self._center_window()
            
            # Configure style
            self._configure_style()
            
            # Create UI elements
            self._create_main_frame()
            self._create_title()
            self._create_settings_section()
            self._create_info_section()
            self._create_buttons()
            
            # Focus on first input
            self.hotkey_entry.focus_set()
            
            self.logger.info("Settings window opened")
            
        except Exception as e:
            self.logger.error(f"Error creating settings window: {e}")
            messagebox.showerror("Error", f"Failed to open settings: {str(e)}")
    
    def _center_window(self) -> None:
        """Center the window on screen."""
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f"{width}x{height}+{x}+{y}")
    
    def _configure_style(self) -> None:
        """Configure window styling."""
        self.window.configure(bg="#f0f0f0")
        
        # Configure ttk styles
        style = ttk.Style()
        style.theme_use('clam')
    
    def _create_main_frame(self) -> None:
        """Create main container frame."""
        self.main_frame = ttk.Frame(self.window, padding=30)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
    
    def _create_title(self) -> None:
        """Create window title."""
        title_frame = ttk.Frame(self.main_frame)
        title_frame.pack(fill=tk.X, pady=(0, 25))
        
        title_label = ttk.Label(
            title_frame,
            text="Application Settings",
            font=("Segoe UI", 16, "bold")
        )
        title_label.pack()
        
        subtitle_label = ttk.Label(
            title_frame,
            text="Configure your text correction preferences",
            font=("Segoe UI", 9),
            foreground="#666666"
        )
        subtitle_label.pack(pady=(5, 0))
    
    def _create_settings_section(self) -> None:
        """Create settings input section."""
        settings_frame = ttk.LabelFrame(self.main_frame, text="Settings", padding=20)
        settings_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Hotkey setting
        hotkey_frame = ttk.Frame(settings_frame)
        hotkey_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(hotkey_frame, text="Hotkey:", font=("Segoe UI", 10, "bold")).pack(anchor=tk.W)
        ttk.Label(
            hotkey_frame,
            text="Global keyboard shortcut to trigger text correction",
            font=("Segoe UI", 9),
            foreground="#666666"
        ).pack(anchor=tk.W, pady=(2, 5))
        
        self.hotkey_entry = ttk.Entry(hotkey_frame, textvariable=self.hotkey_var, width=20)
        self.hotkey_entry.pack(anchor=tk.W)
        
        # Auto paste setting
        auto_paste_frame = ttk.Frame(settings_frame)
        auto_paste_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.auto_paste_check = ttk.Checkbutton(
            auto_paste_frame,
            text="Automatically paste corrected text",
            variable=self.auto_paste_var
        )
        self.auto_paste_check.pack(anchor=tk.W)
        
        ttk.Label(
            auto_paste_frame,
            text="Automatically replace clipboard content and paste after correction",
            font=("Segoe UI", 9),
            foreground="#666666"
        ).pack(anchor=tk.W, padx=(25, 0), pady=(2, 0))
        
        # Notifications setting
        notifications_frame = ttk.Frame(settings_frame)
        notifications_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.notifications_check = ttk.Checkbutton(
            notifications_frame,
            text="Show desktop notifications",
            variable=self.notifications_var
        )
        self.notifications_check.pack(anchor=tk.W)
        
        ttk.Label(
            notifications_frame,
            text="Display notification popups for status updates and results",
            font=("Segoe UI", 9),
            foreground="#666666"
        ).pack(anchor=tk.W, padx=(25, 0), pady=(2, 0))
        
        # Language setting
        language_frame = ttk.Frame(settings_frame)
        language_frame.pack(fill=tk.X, pady=(0, 0))
        
        ttk.Label(language_frame, text="Language:", font=("Segoe UI", 10, "bold")).pack(anchor=tk.W)
        ttk.Label(
            language_frame,
            text="Language for correction prompts and interface",
            font=("Segoe UI", 9),
            foreground="#666666"
        ).pack(anchor=tk.W, pady=(2, 5))
        
        self.language_combo = ttk.Combobox(
            language_frame,
            textvariable=self.language_var,
            values=["Portuguese", "English"],
            state="readonly",
            width=17
        )
        self.language_combo.pack(anchor=tk.W)
    
    def _create_info_section(self) -> None:
        """Create information section."""
        info_frame = ttk.LabelFrame(self.main_frame, text="Information", padding=15)
        info_frame.pack(fill=tk.X, pady=(0, 20))
        
        info_text = (
            "• Use the global hotkey to correct text from clipboard\n"
            "• Copy any text, press the hotkey, and get corrected text\n"
            "• Restart the application after changing the hotkey\n"
            "• Settings are automatically saved when you click Save"
        )
        
        info_label = ttk.Label(
            info_frame,
            text=info_text,
            font=("Segoe UI", 9),
            foreground="#444444",
            justify=tk.LEFT
        )
        info_label.pack(anchor=tk.W)
    
    def _create_buttons(self) -> None:
        """Create action buttons."""
        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Right-aligned button container
        right_buttons = ttk.Frame(button_frame)
        right_buttons.pack(side=tk.RIGHT)
        
        # Cancel button
        cancel_button = ttk.Button(
            right_buttons,
            text="Cancel",
            command=self._on_cancel,
            width=12
        )
        cancel_button.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Save button
        save_button = ttk.Button(
            right_buttons,
            text="Save Settings",
            command=self._on_save,
            width=15
        )
        save_button.pack(side=tk.RIGHT)
        
        # Reset button (left side)
        reset_button = ttk.Button(
            button_frame,
            text="Reset to Defaults",
            command=self._on_reset,
            width=18
        )
        reset_button.pack(side=tk.LEFT)
    
    def _on_save(self) -> None:
        """Handle save button click."""
        try:
            # Validate inputs
            validation_error = self._validate_inputs()
            if validation_error:
                messagebox.showerror("Validation Error", validation_error)
                return
            
            # Create new settings object
            new_settings = AppSettings(
                hotkey=self.hotkey_var.get().strip(),
                auto_paste=self.auto_paste_var.get(),
                show_notifications=self.notifications_var.get(),
                prompt_language=self.language_var.get()
            )
            
            # Call save callback
            self.on_save_callback(new_settings)
            
            self.logger.info("Settings saved successfully")
            self.window.destroy()
            
        except Exception as e:
            error_msg = f"Failed to save settings: {str(e)}"
            self.logger.error(error_msg)
            messagebox.showerror("Error", error_msg)
    
    def _on_cancel(self) -> None:
        """Handle cancel button click."""
        self.logger.info("Settings dialog cancelled")
        self.window.destroy()
    
    def _on_reset(self) -> None:
        """Handle reset button click."""
        try:
            result = messagebox.askyesno(
                "Reset Settings",
                "Are you sure you want to reset all settings to their default values?",
                icon=messagebox.QUESTION
            )
            
            if result:
                # Reset to default values
                from config import DEFAULT_SETTINGS
                self.hotkey_var.set(DEFAULT_SETTINGS["hotkey"])
                self.auto_paste_var.set(DEFAULT_SETTINGS["auto_paste"])
                self.notifications_var.set(DEFAULT_SETTINGS["show_notifications"])
                self.language_var.set(DEFAULT_SETTINGS["prompt_language"])
                
                self.logger.info("Settings reset to defaults")
        
        except Exception as e:
            self.logger.error(f"Error resetting settings: {e}")
    
    def _validate_inputs(self) -> Optional[str]:
        """
        Validate user inputs.
        
        Returns:
            Error message if validation fails, None if valid
        """
        hotkey = self.hotkey_var.get().strip()
        if not hotkey:
            return "Hotkey cannot be empty"
        
        # Basic hotkey format validation
        if '+' not in hotkey and len(hotkey) > 1:
            return "Hotkey should contain modifier keys (e.g., 'alt+s', 'ctrl+shift+c')"
        
        language = self.language_var.get()
        if language not in ["Portuguese", "English"]:
            return "Please select a valid language"
        
        return None


class AboutDialog:
    """
    About dialog showing application information.
    """
    
    def __init__(self, parent: tk.Tk, app_name: str, version: str):
        """
        Initialize about dialog.
        
        Args:
            parent: Parent window
            app_name: Application name
            version: Application version
        """
        self.parent = parent
        self.app_name = app_name
        self.version = version
    
    def show(self) -> None:
        """Display the about dialog."""
        try:
            dialog = tk.Toplevel(self.parent)
            dialog.title(f"About {self.app_name}")
            dialog.geometry("400x300")
            dialog.resizable(False, False)
            dialog.grab_set()
            
            # Center dialog
            self._center_dialog(dialog)
            
            # Create content
            main_frame = ttk.Frame(dialog, padding=30)
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # App name and version
            title_label = ttk.Label(
                main_frame,
                text=self.app_name,
                font=("Segoe UI", 16, "bold")
            )
            title_label.pack(pady=(0, 5))
            
            version_label = ttk.Label(
                main_frame,
                text=f"Version {self.version}",
                font=("Segoe UI", 10)
            )
            version_label.pack(pady=(0, 20))
            
            # Description
            description = (
                "AI-powered text correction tool with global hotkey support.\n\n"
                "Features:\n"
                "• Global hotkey activation\n"
                "• AI-powered text correction using Google Gemini\n"
                "• System tray integration\n"
                "• Customizable settings\n"
                "• Multi-language support\n\n"
                "Built with Python and modern architecture patterns."
            )
            
            desc_label = ttk.Label(
                main_frame,
                text=description,
                font=("Segoe UI", 9),
                justify=tk.LEFT
            )
            desc_label.pack(pady=(0, 20))
            
            # Close button
            close_button = ttk.Button(
                main_frame,
                text="Close",
                command=dialog.destroy,
                width=12
            )
            close_button.pack()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to show about dialog: {str(e)}")
    
    def _center_dialog(self, dialog: tk.Toplevel) -> None:
        """Center dialog on parent window."""
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        
        parent_x = self.parent.winfo_x()
        parent_y = self.parent.winfo_y()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        
        x = parent_x + (parent_width // 2) - (width // 2)
        y = parent_y + (parent_height // 2) - (height // 2)
        
        dialog.geometry(f"{width}x{height}+{x}+{y}")