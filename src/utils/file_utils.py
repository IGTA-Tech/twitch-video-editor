"""File utility functions for StreamCut Pro"""

import os
import subprocess
from pathlib import Path
from typing import List, Optional, Tuple

# Supported video formats
SUPPORTED_FORMATS = {
    '.mp4', '.mkv', '.avi', '.mov', '.flv',
    '.wmv', '.webm', '.m4v', '.mpg', '.mpeg'
}

def is_video_file(file_path: str) -> bool:
    """Check if file is a supported video format"""
    return Path(file_path).suffix.lower() in SUPPORTED_FORMATS

def check_ffmpeg_installed() -> Tuple[bool, Optional[str]]:
    """
    Check if FFmpeg is installed and accessible

    Returns:
        Tuple of (is_installed, version_string)
    """
    try:
        result = subprocess.run(
            ['ffmpeg', '-version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            return True, version_line
        return False, None
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False, None

def get_video_duration(video_path: str) -> Optional[float]:
    """
    Get video duration in seconds using FFprobe

    Args:
        video_path: Path to video file

    Returns:
        Duration in seconds or None if error
    """
    try:
        result = subprocess.run(
            [
                'ffprobe', '-v', 'error',
                '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1',
                video_path
            ],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            return float(result.stdout.strip())
        return None
    except (FileNotFoundError, ValueError, subprocess.TimeoutExpired):
        return None

def format_duration(seconds: float) -> str:
    """
    Format seconds into HH:MM:SS string

    Args:
        seconds: Duration in seconds

    Returns:
        Formatted string like "01:23:45"
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"

def ensure_output_dir(output_path: str) -> Path:
    """
    Ensure output directory exists

    Args:
        output_path: Path to output directory

    Returns:
        Path object
    """
    path = Path(output_path)
    path.mkdir(parents=True, exist_ok=True)
    return path

def get_unique_filename(base_path: str, extension: str = "") -> str:
    """
    Generate unique filename by adding number suffix if file exists

    Args:
        base_path: Base file path without extension
        extension: File extension (including dot)

    Returns:
        Unique file path
    """
    counter = 1
    if not extension:
        path = Path(base_path)
        extension = path.suffix
        base_path = str(path.with_suffix(''))

    output_path = f"{base_path}{extension}"
    while os.path.exists(output_path):
        output_path = f"{base_path}_{counter}{extension}"
        counter += 1

    return output_path

def get_file_size_mb(file_path: str) -> float:
    """Get file size in megabytes"""
    try:
        return os.path.getsize(file_path) / (1024 * 1024)
    except OSError:
        return 0.0
