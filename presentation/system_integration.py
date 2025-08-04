"""
System Integration - VERSÃO CORRIGIDA
======================================
System tray management and global hotkey handling with fallback support
"""

import logging
import threading
import time
from typing import Callable, Optional

try:
    import pystray
    from PIL import Image, ImageDraw
    from pystray import MenuItem as item
    PYSTRAY_AVAILABLE = True
except ImportError:
    PYSTRAY_AVAILABLE = False
    logging.warning("pystray not available - system tray will be disabled")

from pynput import keyboard as pynput_keyboard

from config import (
    TRAY_ICON_SIZE, 
    TRAY_ICON_BACKGROUND_COLOR, 
    TRAY_ICON_TEXT, 
    TRAY_ICON_TEXT_COLOR
)


class SystemTrayManager:
    """
    Manages system tray icon and context menu with fallback support.
    
    Gracefully handles environments where system tray is not available.
    """
    
    def __init__(
        self,
        app_name: str,
        on_settings_callback: Callable[[], None],
        on_about_callback: Optional[Callable[[], None]] = None,
        on_exit_callback: Callable[[], None] = None
    ):
        """Initialize system tray manager with fallback support."""
        self.app_name = app_name
        self.on_settings = on_settings_callback
        self.on_about = on_about_callback
        self.on_exit = on_exit_callback
        
        self.icon: Optional = None
        self.logger = logging.getLogger("SystemTrayManager")
        self._is_running = False
        self._tray_available = PYSTRAY_AVAILABLE
        
        if not self._tray_available:
            self.logger.warning("System tray not available - running in fallback mode")
    
    def setup(self) -> None:
        """Setup and display system tray icon with fallback."""
        if not self._tray_available:
            self.logger.info("System tray disabled - use Ctrl+C to exit")
            self._is_running = True
            return
        
        try:
            # Create icon image
            image = self._create_icon_image()
            
            # Create menu items
            menu_items = self._create_menu_items()
            
            # Create tray icon
            self.icon = pystray.Icon(
                self.app_name,
                image,
                self.app_name,
                menu_items
            )
            
            # Try to run in detached mode with error handling
            try:
                self.icon.run_detached()
                self._is_running = True
                self.logger.info("System tray icon initialized successfully")
            except Exception as e:
                self.logger.error(f"Failed to dock system tray icon: {e}")
                self.logger.info("Continuing without system tray - use Ctrl+C to exit")
                self._is_running = True  # Continue without tray
                
        except Exception as e:
            error_msg = f"Failed to setup system tray: {str(e)}"
            self.logger.error(error_msg)
            self.logger.info("Continuing without system tray - use Ctrl+C to exit")
            self._is_running = True
    
    def _create_icon_image(self) -> Optional[Image.Image]:
        """Create system tray icon image with error handling."""
        if not self._tray_available:
            return None
            
        try:
            # Create image with transparency
            image = Image.new('RGBA', TRAY_ICON_SIZE, (0, 0, 0, 0))
            draw = ImageDraw.Draw(image)
            
            # Calculate dimensions
            width, height = TRAY_ICON_SIZE
            margin = 8
            
            # Draw background circle
            draw.ellipse(
                [margin, margin, width - margin, height - margin],
                fill=TRAY_ICON_BACKGROUND_COLOR
            )
            
            # Draw text
            text = TRAY_ICON_TEXT
            
            # Calculate text position (center)
            text_width = len(text) * 8  # Rough estimate
            text_height = 12
            text_x = (width - text_width) // 2
            text_y = (height - text_height) // 2
            
            draw.text(
                (text_x, text_y),
                text,
                fill=TRAY_ICON_TEXT_COLOR
            )
            
            return image
            
        except Exception as e:
            self.logger.error(f"Failed to create icon image: {e}")
            return None
    
    def _create_menu_items(self) -> tuple:
        """Create context menu items for tray icon."""
        menu_items = []
        
        # Settings item
        if self.on_settings:
            menu_items.append(item('Settings', self.on_settings))
        
        # About item (if callback provided)
        if self.on_about:
            menu_items.append(item('About', self.on_about))
        
        # Separator
        if menu_items:
            menu_items.append(item('---', None))  # Separator
        
        # Exit item
        if self.on_exit:
            menu_items.append(item('Exit', self.on_exit))
        
        return tuple(menu_items)
    
    def show_notification(self, title: str, message: str, duration: int = 3) -> None:
        """Show system tray notification with fallback."""
        try:
            if self.icon and self._is_running and self._tray_available:
                self.icon.notify(message, title)
                self.logger.debug(f"Tray notification shown: {title}")
            else:
                # Fallback: log the notification
                self.logger.info(f"NOTIFICATION: {title} - {message}")
        except Exception as e:
            self.logger.error(f"Failed to show tray notification: {e}")
            self.logger.info(f"NOTIFICATION: {title} - {message}")
    
    def stop(self) -> None:
        """Stop and remove system tray icon."""
        try:
            if self.icon and self._is_running and self._tray_available:
                self.icon.stop()
                self.logger.info("System tray icon stopped")
            self._is_running = False
        except Exception as e:
            self.logger.error(f"Error stopping tray icon: {e}")
            self._is_running = False
    
    @property
    def is_running(self) -> bool:
        """Check if tray manager is running."""
        return self._is_running


class HotkeyListener:
    """
    Global hotkey detection and handling.
    
    Listens for global keyboard shortcuts and triggers callbacks
    when specific key combinations are pressed.
    """
    
    def __init__(self, hotkey: str, callback: Callable[[], None]):
        """
        Initialize hotkey listener.
        
        Args:
            hotkey: Hotkey combination (e.g., 'alt+s', 'ctrl+shift+c')
            callback: Function to call when hotkey is pressed
        """
        self.hotkey = hotkey
        self.callback = callback
        self.stop_event = threading.Event()
        self.logger = logging.getLogger("HotkeyListener")
        self._listener: Optional[pynput_keyboard.Listener] = None
        self._is_running = False
    
    def start(self) -> None:
        """Start global hotkey listener."""
        try:
            # Normalize hotkey format
            normalized_hotkey = self._normalize_hotkey(self.hotkey)
            self.logger.info(f"Starting hotkey listener for: {self.hotkey} ({normalized_hotkey})")
            
            # Create hotkey object
            hotkey_obj = pynput_keyboard.HotKey(
                pynput_keyboard.HotKey.parse(normalized_hotkey),
                self._on_hotkey_pressed
            )
            
            # Create listener
            def for_canonical(f):
                return lambda k: f(self._listener.canonical(k))
            
            self._listener = pynput_keyboard.Listener(
                on_press=for_canonical(hotkey_obj.press),
                on_release=for_canonical(hotkey_obj.release)
            )
            
            # Start listener
            self._listener.start()
            self._is_running = True
            
            self.logger.info("Hotkey listener started successfully")
            
            # Keep listener running until stop event
            while not self.stop_event.is_set():
                time.sleep(0.1)
            
            # Stop listener
            if self._listener:
                self._listener.stop()
                self._is_running = False
            
            self.logger.info("Hotkey listener stopped")
            
        except Exception as e:
            error_msg = f"Hotkey listener error: {str(e)}"
            self.logger.error(error_msg)
            self._is_running = False
            raise Exception(error_msg)
    
    def _normalize_hotkey(self, hotkey: str) -> str:
        """
        Normalize hotkey format for pynput compatibility.
        
        Args:
            hotkey: Raw hotkey string
            
        Returns:
            Normalized hotkey string
        """
        # Convert to lowercase and split by '+'
        keys = hotkey.lower().strip().split('+')
        
        # Normalize each key
        normalized_keys = []
        for key in keys:
            key = key.strip()
            if len(key) > 1:  # Modifier key
                normalized_keys.append(f'<{key}>')
            else:  # Regular key
                normalized_keys.append(key)
        
        return '+'.join(normalized_keys)
    
    def _on_hotkey_pressed(self) -> None:
        """Handle hotkey press event."""
        try:
            self.logger.info(f"Hotkey pressed: {self.hotkey}")
            
            # Call the callback in a separate thread to avoid blocking
            callback_thread = threading.Thread(
                target=self._safe_callback,
                daemon=True
            )
            callback_thread.start()
            
        except Exception as e:
            self.logger.error(f"Error handling hotkey press: {e}")
    
    def _safe_callback(self) -> None:
        """Safely execute callback with error handling."""
        try:
            self.callback()
        except Exception as e:
            self.logger.error(f"Error in hotkey callback: {e}")
    
    def stop(self) -> None:
        """Stop hotkey listener."""
        self.logger.info("Stopping hotkey listener...")
        self.stop_event.set()
    
    @property
    def is_running(self) -> bool:
        """Check if hotkey listener is running."""
        return self._is_running
    
    def test_hotkey_format(self) -> bool:
        """
        Test if hotkey format is valid.
        
        Returns:
            True if format is valid, False otherwise
        """
        try:
            normalized = self._normalize_hotkey(self.hotkey)
            pynput_keyboard.HotKey.parse(normalized)
            return True
        except Exception as e:
            self.logger.warning(f"Invalid hotkey format '{self.hotkey}': {e}")
            return False


class WindowManager:
    """
    Manages application windows and their states.
    
    Provides utilities for window positioning, focus management,
    and window state tracking.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("WindowManager")
        self.active_windows = {}
    
    def register_window(self, name: str, window) -> None:
        """
        Register a window for management.
        
        Args:
            name: Unique name for the window
            window: Window object to register
        """
        self.active_windows[name] = window
        self.logger.debug(f"Window registered: {name}")
    
    def unregister_window(self, name: str) -> None:
        """
        Unregister a window.
        
        Args:
            name: Name of window to unregister
        """
        if name in self.active_windows:
            del self.active_windows[name]
            self.logger.debug(f"Window unregistered: {name}")
    
    def get_window(self, name: str):
        """
        Get registered window by name.
        
        Args:
            name: Window name
            
        Returns:
            Window object or None if not found
        """
        return self.active_windows.get(name)
    
    def close_all_windows(self) -> None:
        """Close all registered windows."""
        for name, window in list(self.active_windows.items()):
            try:
                if hasattr(window, 'destroy'):
                    window.destroy()
                elif hasattr(window, 'close'):
                    window.close()
                self.logger.debug(f"Closed window: {name}")
            except Exception as e:
                self.logger.error(f"Error closing window {name}: {e}")
        
        self.active_windows.clear()
    
    def bring_to_front(self, name: str) -> bool:
        """
        Bring window to front.
        
        Args:
            name: Window name
            
        Returns:
            True if successful, False otherwise
        """
        try:
            window = self.get_window(name)
            if window and hasattr(window, 'lift'):
                window.lift()
                window.focus_force()
                self.logger.debug(f"Brought window to front: {name}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error bringing window to front: {e}")
            return False
    
    def minimize_all(self) -> None:
        """Minimize all registered windows."""
        for name, window in self.active_windows.items():
            try:
                if hasattr(window, 'iconify'):
                    window.iconify()
                    self.logger.debug(f"Minimized window: {name}")
            except Exception as e:
                self.logger.error(f"Error minimizing window {name}: {e}")
    
    def get_window_count(self) -> int:
        """Get count of active windows."""
        return len(self.active_windows)
    
    def get_window_list(self) -> list:
        """Get list of active window names."""
        return list(self.active_windows.keys())