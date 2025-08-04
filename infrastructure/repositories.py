"""
Repositories
============
Data persistence implementations
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any

from domain.models import AppSettings
from config import DEFAULT_SETTINGS


class SettingsRepository:
    """
    Repository for persisting application settings to JSON file.
    
    This class handles the storage and retrieval of application settings,
    providing a clean interface for settings persistence.
    """
    
    def __init__(self, config_path: str = "settings.json"):
        """
        Initialize settings repository.
        
        Args:
            config_path: Path to the settings JSON file
        """
        self.config_path = Path(config_path)
        self.logger = logging.getLogger("SettingsRepository")
        
        # Ensure the directory exists
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
    
    def load(self) -> AppSettings:
        """
        Load application settings from file.
        
        Returns:
            AppSettings object with loaded or default settings
        """
        try:
            if self.config_path.exists():
                self.logger.info(f"Loading settings from {self.config_path}")
                
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Merge with defaults to handle missing keys
                merged_data = {**DEFAULT_SETTINGS, **data}
                settings = AppSettings.from_dict(merged_data)
                
                self.logger.info("Settings loaded successfully")
                return settings
            else:
                self.logger.info("Settings file not found, using defaults")
                return AppSettings.from_dict(DEFAULT_SETTINGS)
                
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON in settings file: {e}")
            self._backup_corrupted_file()
            return AppSettings.from_dict(DEFAULT_SETTINGS)
            
        except Exception as e:
            self.logger.error(f"Error loading settings: {e}")
            return AppSettings.from_dict(DEFAULT_SETTINGS)
    
    def save(self, settings: AppSettings) -> None:
        """
        Save application settings to file.
        
        Args:
            settings: AppSettings object to save
            
        Raises:
            Exception: If saving fails
        """
        try:
            # Convert settings to dictionary
            settings_dict = settings.to_dict()
            
            # Write to temporary file first (atomic write)
            temp_path = self.config_path.with_suffix('.tmp')
            
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(settings_dict, f, indent=4, ensure_ascii=False)
            
            # Atomically replace the original file
            temp_path.replace(self.config_path)
            
            self.logger.info(f"Settings saved successfully to {self.config_path}")
            
        except Exception as e:
            error_msg = f"Failed to save settings: {str(e)}"
            self.logger.error(error_msg)
            
            # Clean up temporary file if it exists
            temp_path = self.config_path.with_suffix('.tmp')
            if temp_path.exists():
                try:
                    temp_path.unlink()
                except:
                    pass
            
            raise Exception(error_msg)
    
    def backup(self) -> bool:
        """
        Create a backup of current settings file.
        
        Returns:
            True if backup was created successfully, False otherwise
        """
        try:
            if not self.config_path.exists():
                self.logger.warning("No settings file to backup")
                return False
            
            backup_path = self.config_path.with_suffix('.backup')
            
            # Copy current settings to backup
            import shutil
            shutil.copy2(self.config_path, backup_path)
            
            self.logger.info(f"Settings backup created: {backup_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create backup: {e}")
            return False
    
    def restore_from_backup(self) -> bool:
        """
        Restore settings from backup file.
        
        Returns:
            True if restored successfully, False otherwise
        """
        try:
            backup_path = self.config_path.with_suffix('.backup')
            
            if not backup_path.exists():
                self.logger.error("No backup file found")
                return False
            
            # Copy backup to main settings file
            import shutil
            shutil.copy2(backup_path, self.config_path)
            
            self.logger.info("Settings restored from backup")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to restore from backup: {e}")
            return False
    
    def _backup_corrupted_file(self) -> None:
        """Backup corrupted settings file for debugging."""
        try:
            if self.config_path.exists():
                corrupted_path = self.config_path.with_suffix('.corrupted')
                import shutil
                shutil.copy2(self.config_path, corrupted_path)
                self.logger.info(f"Corrupted file backed up to: {corrupted_path}")
        except Exception as e:
            self.logger.error(f"Failed to backup corrupted file: {e}")
    
    def reset_to_defaults(self) -> None:
        """Reset settings to default values."""
        try:
            default_settings = AppSettings.from_dict(DEFAULT_SETTINGS)
            self.save(default_settings)
            self.logger.info("Settings reset to defaults")
        except Exception as e:
            self.logger.error(f"Failed to reset settings: {e}")
    
    def get_file_info(self) -> Dict[str, Any]:
        """
        Get information about the settings file.
        
        Returns:
            Dictionary with file information
        """
        info = {
            "path": str(self.config_path),
            "exists": self.config_path.exists(),
            "size": 0,
            "modified": None,
            "readable": False,
            "writable": False
        }
        
        try:
            if self.config_path.exists():
                stat = self.config_path.stat()
                info.update({
                    "size": stat.st_size,
                    "modified": stat.st_mtime,
                    "readable": self.config_path.is_file() and 
                               self.config_path.stat().st_mode & 0o444,
                    "writable": self.config_path.is_file() and 
                               self.config_path.stat().st_mode & 0o200
                })
        except Exception as e:
            self.logger.error(f"Error getting file info: {e}")
        
        return info


class LogRepository:
    """
    Repository for managing application logs.
    
    This class provides utilities for log file management,
    rotation, and cleanup.
    """
    
    def __init__(self, log_path: str = "text_correction.log"):
        """
        Initialize log repository.
        
        Args:
            log_path: Path to the log file
        """
        self.log_path = Path(log_path)
        self.logger = logging.getLogger("LogRepository")
        
        # Ensure log directory exists
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
    
    def get_log_size(self) -> int:
        """
        Get current log file size in bytes.
        
        Returns:
            File size in bytes, 0 if file doesn't exist
        """
        try:
            if self.log_path.exists():
                return self.log_path.stat().st_size
            return 0
        except Exception:
            return 0
    
    def rotate_log(self, max_size: int = 10 * 1024 * 1024) -> bool:
        """
        Rotate log file if it exceeds max size.
        
        Args:
            max_size: Maximum file size in bytes before rotation
            
        Returns:
            True if rotation was performed, False otherwise
        """
        try:
            if not self.log_path.exists():
                return False
            
            current_size = self.get_log_size()
            if current_size < max_size:
                return False
            
            # Create rotated log name with timestamp
            import time
            timestamp = int(time.time())
            rotated_path = self.log_path.with_suffix(f'.{timestamp}.log')
            
            # Move current log to rotated name
            self.log_path.rename(rotated_path)
            
            self.logger.info(f"Log rotated to: {rotated_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Log rotation failed: {e}")
            return False
    
    def cleanup_old_logs(self, keep_count: int = 5) -> int:
        """
        Clean up old rotated log files.
        
        Args:
            keep_count: Number of rotated logs to keep
            
        Returns:
            Number of files cleaned up
        """
        try:
            # Find all rotated log files
            log_pattern = f"{self.log_path.stem}.*.log"
            rotated_logs = list(self.log_path.parent.glob(log_pattern))
            
            if len(rotated_logs) <= keep_count:
                return 0
            
            # Sort by modification time (oldest first)
            rotated_logs.sort(key=lambda p: p.stat().st_mtime)
            
            # Remove oldest files
            cleanup_count = 0
            for log_file in rotated_logs[:-keep_count]:
                try:
                    log_file.unlink()
                    cleanup_count += 1
                except Exception as e:
                    self.logger.error(f"Failed to remove {log_file}: {e}")
            
            if cleanup_count > 0:
                self.logger.info(f"Cleaned up {cleanup_count} old log files")
            
            return cleanup_count
            
        except Exception as e:
            self.logger.error(f"Log cleanup failed: {e}")
            return 0