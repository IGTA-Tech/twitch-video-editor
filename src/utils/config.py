"""Configuration management for StreamCut Pro"""

import json
import os
from pathlib import Path
from typing import Dict, Any

class Config:
    """Manages application configuration"""

    DEFAULT_CONFIG = {
        "processing_mode": "ffmpeg",
        "silence_threshold_db": -30,
        "min_silence_duration": 2.0,
        "padding_seconds": 0.5,
        "whisper_model": "base",
        "export_clips": True,
        "export_merged": True,
        "export_timestamps": True,
        "export_xml": False,
        "output_folder": "./output",
        "ffmpeg_path": "ffmpeg",
        "threads": 4,
        "window_geometry": "900x700"
    }

    def __init__(self, config_path: str = "config/settings.json"):
        self.config_path = Path(config_path)
        self.config: Dict[str, Any] = self.DEFAULT_CONFIG.copy()
        self.load()

    def load(self) -> None:
        """Load configuration from file"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    loaded_config = json.load(f)
                    self.config.update(loaded_config)
            except Exception as e:
                print(f"Error loading config: {e}")
                print("Using default configuration")

    def save(self) -> None:
        """Save configuration to file"""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self.config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set configuration value"""
        self.config[key] = value

    def update(self, updates: Dict[str, Any]) -> None:
        """Update multiple configuration values"""
        self.config.update(updates)
