"""
Infrastructure Services - VERSÃO CORRIGIDA PARA LINUX
=====================================================
Technical services and external integrations with robust clipboard support
"""

import logging
import subprocess
import sys
from typing import Optional

from pynput import keyboard as pynput_keyboard

from config import LOG_FORMAT, LOG_LEVEL


class LoggingService:
    """
    Service for configuring application logging.
    
    Provides centralized logging configuration with file and console output.
    """
    
    @staticmethod
    def setup(app_name: str, log_file: str = "app.log", level: str = LOG_LEVEL) -> None:
        """
        Setup application logging configuration.
        
        Args:
            app_name: Name of the application for logger identification
            log_file: Path to log file
            level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        # Convert string level to logging constant
        numeric_level = getattr(logging, level.upper(), logging.INFO)
        
        # Create formatters
        file_formatter = logging.Formatter(LOG_FORMAT)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        
        # Setup file handler
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(file_formatter)
        
        # Setup console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(numeric_level)
        console_handler.setFormatter(console_formatter)
        
        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(numeric_level)
        root_logger.handlers.clear()  # Remove any existing handlers
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)
        
        # Log startup message
        logger = logging.getLogger(app_name)
        logger.info(f"Logging configured - Level: {level}, File: {log_file}")
    
    @staticmethod
    def get_logger(name: str) -> logging.Logger:
        """
        Get a logger instance with the specified name.
        
        Args:
            name: Logger name
            
        Returns:
            Logger instance
        """
        return logging.getLogger(name)


class ClipboardService:
    """
    Service for clipboard operations with robust Linux support.
    
    Implements multiple clipboard backends for cross-platform compatibility.
    Automatically detects and uses the best available method.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("ClipboardService")
        self.clipboard_backend = None
        self._initialize_clipboard_backend()
    
    def _initialize_clipboard_backend(self) -> None:
        """Initialize the best available clipboard backend."""
        backends = [
            ("pyclip", self._init_pyclip),
            ("xclip", self._init_xclip),
            ("xsel", self._init_xsel),
            ("pyperclip", self._init_pyperclip),
        ]
        
        for backend_name, init_func in backends:
            try:
                if init_func():
                    self.clipboard_backend = backend_name
                    self.logger.info(f"Using clipboard backend: {backend_name}")
                    return
            except Exception as e:
                self.logger.debug(f"Failed to initialize {backend_name}: {e}")
        
        self.logger.warning("No working clipboard backend found - clipboard functionality may be limited")
        self.clipboard_backend = "none"
    
    def _init_pyclip(self) -> bool:
        """Try to initialize pyclip backend."""
        try:
            import pyclip
            self._pyclip = pyclip
            
            # Test basic functionality
            test_text = "test"
            pyclip.copy(test_text)
            result = pyclip.paste()
            
            return True
        except ImportError:
            self.logger.debug("pyclip not available - install with: pip install pyclip")
            return False
        except Exception as e:
            self.logger.debug(f"pyclip test failed: {e}")
            return False
    
    def _init_xclip(self) -> bool:
        """Try to initialize xclip backend."""
        try:
            # Check if xclip is available
            subprocess.run(['xclip', '-version'], 
                         capture_output=True, check=True, timeout=2)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            self.logger.debug("xclip not available - install with: sudo pacman -S xclip")
            return False
    
    def _init_xsel(self) -> bool:
        """Try to initialize xsel backend."""
        try:
            # Check if xsel is available
            subprocess.run(['xsel', '--version'], 
                         capture_output=True, check=True, timeout=2)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            self.logger.debug("xsel not available - install with: sudo pacman -S xsel")
            return False
    
    def _init_pyperclip(self) -> bool:
        """Try to initialize pyperclip backend."""
        try:
            import pyperclip
            
            # Test basic functionality
            test_text = "test"
            pyperclip.copy(test_text)
            result = pyperclip.paste()
            
            self._pyperclip = pyperclip
            return True
        except Exception as e:
            self.logger.debug(f"pyperclip failed: {e}")
            return False
    
    def get_text(self) -> str:
        """
        Get text from clipboard using the best available backend.
        
        Returns:
            Clipboard text content, empty string on error
        """
        try:
            if self.clipboard_backend == "pyclip":
                return self._get_text_pyclip()
            elif self.clipboard_backend == "xclip":
                return self._get_text_xclip()
            elif self.clipboard_backend == "xsel":
                return self._get_text_xsel()
            elif self.clipboard_backend == "pyperclip":
                return self._get_text_pyperclip()
            else:
                self.logger.warning("No clipboard backend available")
                return ""
                
        except Exception as e:
            self.logger.error(f"Error getting clipboard text: {e}")
            return ""
    
    def _get_text_pyclip(self) -> str:
        """Get text using pyclip."""
        text = self._pyclip.paste()
        self.logger.debug(f"Retrieved {len(text)} characters from clipboard (pyclip)")
        return text if text else ""
    
    def _get_text_xclip(self) -> str:
        """Get text using xclip command."""
        try:
            result = subprocess.run(
                ['xclip', '-selection', 'clipboard', '-o'],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                text = result.stdout
                self.logger.debug(f"Retrieved {len(text)} characters from clipboard (xclip)")
                return text
            else:
                self.logger.warning(f"xclip failed with return code {result.returncode}")
                return ""
        except subprocess.TimeoutExpired:
            self.logger.error("xclip timeout")
            return ""
    
    def _get_text_xsel(self) -> str:
        """Get text using xsel command."""
        try:
            result = subprocess.run(
                ['xsel', '--clipboard', '--output'],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                text = result.stdout
                self.logger.debug(f"Retrieved {len(text)} characters from clipboard (xsel)")
                return text
            else:
                self.logger.warning(f"xsel failed with return code {result.returncode}")
                return ""
        except subprocess.TimeoutExpired:
            self.logger.error("xsel timeout")
            return ""
    
    def _get_text_pyperclip(self) -> str:
        """Get text using pyperclip."""
        text = self._pyperclip.paste()
        self.logger.debug(f"Retrieved {len(text)} characters from clipboard (pyperclip)")
        return text if text else ""
    
    def set_text(self, text: str) -> bool:
        """
        Set text to clipboard using the best available backend.
        
        Args:
            text: Text to copy to clipboard
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not isinstance(text, str):
                text = str(text)
            
            if self.clipboard_backend == "pyclip":
                return self._set_text_pyclip(text)
            elif self.clipboard_backend == "xclip":
                return self._set_text_xclip(text)
            elif self.clipboard_backend == "xsel":
                return self._set_text_xsel(text)
            elif self.clipboard_backend == "pyperclip":
                return self._set_text_pyperclip(text)
            else:
                self.logger.warning("No clipboard backend available")
                return False
                
        except Exception as e:
            self.logger.error(f"Error setting clipboard text: {e}")
            return False
    
    def _set_text_pyclip(self, text: str) -> bool:
        """Set text using pyclip."""
        self._pyclip.copy(text)
        self.logger.debug(f"Copied {len(text)} characters to clipboard (pyclip)")
        return True
    
    def _set_text_xclip(self, text: str) -> bool:
        """Set text using xclip command."""
        try:
            process = subprocess.Popen(
                ['xclip', '-selection', 'clipboard'],
                stdin=subprocess.PIPE, text=True
            )
            process.communicate(input=text, timeout=5)
            
            if process.returncode == 0:
                self.logger.debug(f"Copied {len(text)} characters to clipboard (xclip)")
                return True
            else:
                self.logger.warning(f"xclip failed with return code {process.returncode}")
                return False
        except subprocess.TimeoutExpired:
            self.logger.error("xclip timeout")
            return False
    
    def _set_text_xsel(self, text: str) -> bool:
        """Set text using xsel command."""
        try:
            process = subprocess.Popen(
                ['xsel', '--clipboard', '--input'],
                stdin=subprocess.PIPE, text=True
            )
            process.communicate(input=text, timeout=5)
            
            if process.returncode == 0:
                self.logger.debug(f"Copied {len(text)} characters to clipboard (xsel)")
                return True
            else:
                self.logger.warning(f"xsel failed with return code {process.returncode}")
                return False
        except subprocess.TimeoutExpired:
            self.logger.error("xsel timeout")
            return False
    
    def _set_text_pyperclip(self, text: str) -> bool:
        """Set text using pyperclip."""
        self._pyperclip.copy(text)
        self.logger.debug(f"Copied {len(text)} characters to clipboard (pyperclip)")
        return True
    
    async def paste(self) -> bool:
        """
        Simulate paste operation (Ctrl+V).
        
        Returns:
            True if successful, False otherwise
        """
        try:
            with pynput_keyboard.Controller() as controller:
                # Press Ctrl+V
                controller.press(pynput_keyboard.Key.ctrl)
                controller.press('v')
                controller.release('v')
                controller.release(pynput_keyboard.Key.ctrl)
            
            self.logger.debug("Paste operation completed")
            return True
            
        except Exception as e:
            self.logger.error(f"Error performing paste operation: {e}")
            return False
    
    def get_clipboard_info(self) -> dict:
        """
        Get information about current clipboard state.
        
        Returns:
            Dictionary with clipboard information
        """
        try:
            text = self.get_text()
            return {
                "has_content": bool(text),
                "content_length": len(text),
                "content_type": "text",
                "preview": text[:50] + "..." if len(text) > 50 else text,
                "backend": self.clipboard_backend
            }
        except Exception as e:
            return {
                "has_content": False,
                "content_length": 0,
                "content_type": "unknown",
                "backend": self.clipboard_backend,
                "error": str(e)
            }


# Resto das classes permanecem iguais...
class SystemIntegrationService:
    """
    Service for system-level integrations and utilities.
    
    Provides system information and integration capabilities.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("SystemIntegrationService")
    
    def get_system_info(self) -> dict:
        """
        Get system information.
        
        Returns:
            Dictionary with system information
        """
        import platform
        import os
        
        try:
            return {
                "platform": platform.system(),
                "platform_version": platform.version(),
                "architecture": platform.architecture()[0],
                "processor": platform.processor(),
                "python_version": platform.python_version(),
                "user": os.getenv('USERNAME') or os.getenv('USER', 'unknown'),
                "working_directory": os.getcwd()
            }
        except Exception as e:
            self.logger.error(f"Error getting system info: {e}")
            return {"error": str(e)}
    
    def check_dependencies(self) -> dict:
        """
        Check if all required dependencies are available.
        
        Returns:
            Dictionary with dependency status
        """
        dependencies = {
            "pyclip": False,
            "pyperclip": False,
            "pynput": False,
            "PIL": False,
            "pystray": False,
            "google.generativeai": False,
            "tkinter": False,
            "xclip": False,
            "xsel": False
        }
        
        # Test Python dependencies
        try:
            import pyclip
            dependencies["pyclip"] = True
        except ImportError:
            pass
        
        try:
            import pyperclip
            dependencies["pyperclip"] = True
        except ImportError:
            pass
        
        try:
            import pynput
            dependencies["pynput"] = True
        except ImportError:
            pass
        
        try:
            from PIL import Image
            dependencies["PIL"] = True
        except ImportError:
            pass
        
        try:
            import pystray
            dependencies["pystray"] = True
        except ImportError:
            pass
        
        try:
            import google.generativeai
            dependencies["google.generativeai"] = True
        except ImportError:
            pass
        
        try:
            import tkinter
            dependencies["tkinter"] = True
        except ImportError:
            pass
        
        # Test system clipboard tools
        try:
            subprocess.run(['xclip', '-version'], 
                         capture_output=True, check=True, timeout=2)
            dependencies["xclip"] = True
        except:
            pass
        
        try:
            subprocess.run(['xsel', '--version'], 
                         capture_output=True, check=True, timeout=2)
            dependencies["xsel"] = True
        except:
            pass
        
        return dependencies
    
    def is_running_as_admin(self) -> bool:
        """
        Check if application is running with administrator privileges.
        
        Returns:
            True if running as admin, False otherwise
        """
        try:
            import os
            if os.name == 'nt':  # Windows
                import ctypes
                return ctypes.windll.shell32.IsUserAnAdmin() != 0
            else:  # Unix-like systems
                return os.getuid() == 0
        except Exception:
            return False
    
    def get_startup_info(self) -> dict:
        """
        Get application startup information.
        
        Returns:
            Dictionary with startup information
        """
        import time
        import os
        
        return {
            "startup_time": time.time(),
            "pid": os.getpid(),
            "working_directory": os.getcwd(),
            "python_executable": sys.executable,
            "command_line": sys.argv,
            "is_admin": self.is_running_as_admin()
        }


class PerformanceMonitor:
    """
    Service for monitoring application performance.
    
    Tracks metrics like memory usage, processing time, and operation counts.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("PerformanceMonitor")
        self.metrics = {
            "corrections_processed": 0,
            "total_processing_time": 0.0,
            "average_processing_time": 0.0,
            "errors_count": 0,
            "startup_time": None
        }
        self.start_time = None
    
    def start_monitoring(self) -> None:
        """Start performance monitoring."""
        import time
        self.start_time = time.time()
        self.metrics["startup_time"] = self.start_time
        self.logger.info("Performance monitoring started")
    
    def record_correction(self, processing_time: float, success: bool) -> None:
        """
        Record a text correction operation.
        
        Args:
            processing_time: Time taken for the correction
            success: Whether the correction was successful
        """
        self.metrics["corrections_processed"] += 1
        
        if success:
            self.metrics["total_processing_time"] += processing_time
            self.metrics["average_processing_time"] = (
                self.metrics["total_processing_time"] / 
                max(1, self.metrics["corrections_processed"])
            )
        else:
            self.metrics["errors_count"] += 1
        
        self.logger.debug(f"Recorded correction: {processing_time:.2f}s, success: {success}")
    
    def get_metrics(self) -> dict:
        """
        Get current performance metrics.
        
        Returns:
            Dictionary with performance metrics
        """
        import time
        
        metrics = self.metrics.copy()
        
        if self.start_time:
            metrics["uptime"] = time.time() - self.start_time
            
            # Calculate success rate
            total_operations = metrics["corrections_processed"]
            if total_operations > 0:
                metrics["success_rate"] = (
                    (total_operations - metrics["errors_count"]) / total_operations
                ) * 100
            else:
                metrics["success_rate"] = 0.0
        
        return metrics
    
    def get_memory_usage(self) -> dict:
        """
        Get current memory usage information.
        
        Returns:
            Dictionary with memory usage info
        """
        try:
            import psutil
            import os
            
            process = psutil.Process(os.getpid())
            memory_info = process.memory_info()
            
            return {
                "rss": memory_info.rss,  # Resident Set Size
                "vms": memory_info.vms,  # Virtual Memory Size
                "percent": process.memory_percent(),
                "available": psutil.virtual_memory().available
            }
        except ImportError:
            # psutil not available, use basic info
            import os
            return {
                "pid": os.getpid(),
                "psutil_available": False
            }
        except Exception as e:
            self.logger.error(f"Error getting memory usage: {e}")
            return {"error": str(e)}