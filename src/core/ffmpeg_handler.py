"""FFmpeg handler for video processing and silence detection"""

import subprocess
import re
from pathlib import Path
from typing import List, Tuple, Optional, Callable
import json

class FFmpegHandler:
    """Handles FFmpeg operations for video processing"""

    def __init__(self, ffmpeg_path: str = "ffmpeg"):
        self.ffmpeg_path = ffmpeg_path
        self.ffprobe_path = "ffprobe"

    def detect_silence(
        self,
        video_path: str,
        threshold_db: float = -30,
        min_duration: float = 2.0,
        progress_callback: Optional[Callable[[str], None]] = None
    ) -> List[Tuple[float, float]]:
        """
        Detect silent segments in video

        Args:
            video_path: Path to video file
            threshold_db: Noise threshold in dB (e.g., -30)
            min_duration: Minimum silence duration in seconds
            progress_callback: Optional callback for progress updates

        Returns:
            List of (start_time, end_time) tuples for silent segments
        """
        if progress_callback:
            progress_callback("Analyzing audio for silence...")

        cmd = [
            self.ffmpeg_path,
            '-i', video_path,
            '-af', f'silencedetect=noise={threshold_db}dB:d={min_duration}',
            '-f', 'null',
            '-'
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=None
            )

            # Parse silence detection output
            silence_segments = []
            silence_start = None

            for line in result.stderr.split('\n'):
                if 'silence_start' in line:
                    match = re.search(r'silence_start: ([\d.]+)', line)
                    if match:
                        silence_start = float(match.group(1))

                elif 'silence_end' in line and silence_start is not None:
                    match = re.search(r'silence_end: ([\d.]+)', line)
                    if match:
                        silence_end = float(match.group(1))
                        silence_segments.append((silence_start, silence_end))
                        silence_start = None

            if progress_callback:
                progress_callback(f"Found {len(silence_segments)} silent segments")

            return silence_segments

        except subprocess.TimeoutExpired:
            if progress_callback:
                progress_callback("Error: Processing timeout")
            return []
        except Exception as e:
            if progress_callback:
                progress_callback(f"Error detecting silence: {str(e)}")
            return []

    def get_video_info(self, video_path: str) -> dict:
        """Get video metadata using ffprobe"""
        cmd = [
            self.ffprobe_path,
            '-v', 'quiet',
            '-print_format', 'json',
            '-show_format',
            '-show_streams',
            video_path
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                return json.loads(result.stdout)
            return {}
        except Exception:
            return {}

    def cut_video(
        self,
        video_path: str,
        keep_segments: List[Tuple[float, float]],
        output_path: str,
        padding: float = 0.5,
        progress_callback: Optional[Callable[[str], None]] = None
    ) -> bool:
        """
        Cut video keeping only specified segments

        Args:
            video_path: Input video path
            keep_segments: List of (start, end) tuples to keep
            output_path: Output file path
            padding: Seconds to keep before/after each segment
            progress_callback: Optional callback for progress updates

        Returns:
            True if successful
        """
        if not keep_segments:
            if progress_callback:
                progress_callback("No segments to keep")
            return False

        if progress_callback:
            progress_callback(f"Creating video with {len(keep_segments)} segments...")

        # Build filter complex for cutting
        filter_parts = []
        for i, (start, end) in enumerate(keep_segments):
            # Apply padding
            padded_start = max(0, start - padding)
            padded_end = end + padding

            filter_parts.append(
                f"[0:v]trim=start={padded_start}:end={padded_end},setpts=PTS-STARTPTS[v{i}];"
                f"[0:a]atrim=start={padded_start}:end={padded_end},asetpts=PTS-STARTPTS[a{i}]"
            )

        # Concatenate all segments
        v_inputs = ''.join([f"[v{i}]" for i in range(len(keep_segments))])
        a_inputs = ''.join([f"[a{i}]" for i in range(len(keep_segments))])
        filter_complex = ';'.join(filter_parts)
        filter_complex += f";{v_inputs}concat=n={len(keep_segments)}:v=1:a=0[outv];"
        filter_complex += f"{a_inputs}concat=n={len(keep_segments)}:v=0:a=1[outa]"

        cmd = [
            self.ffmpeg_path,
            '-i', video_path,
            '-filter_complex', filter_complex,
            '-map', '[outv]',
            '-map', '[outa]',
            '-c:v', 'libx264',
            '-crf', '23',
            '-preset', 'medium',
            '-c:a', 'aac',
            '-b:a', '192k',
            '-y',
            output_path
        ]

        try:
            # Run ffmpeg with progress monitoring
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                universal_newlines=True
            )

            # Monitor progress
            for line in process.stderr:
                if progress_callback and 'time=' in line:
                    time_match = re.search(r'time=(\d{2}):(\d{2}):(\d{2})', line)
                    if time_match:
                        h, m, s = map(int, time_match.groups())
                        current_time = h * 3600 + m * 60 + s
                        progress_callback(f"Processing... {current_time}s")

            process.wait()

            if process.returncode == 0:
                if progress_callback:
                    progress_callback("Video created successfully!")
                return True
            else:
                if progress_callback:
                    progress_callback(f"Error: FFmpeg returned code {process.returncode}")
                return False

        except Exception as e:
            if progress_callback:
                progress_callback(f"Error cutting video: {str(e)}")
            return False

    def export_clips(
        self,
        video_path: str,
        segments: List[Tuple[float, float]],
        output_dir: str,
        base_name: str,
        padding: float = 0.5,
        progress_callback: Optional[Callable[[str, int, int], None]] = None
    ) -> List[str]:
        """
        Export individual clips

        Args:
            video_path: Input video path
            segments: List of (start, end) tuples
            output_dir: Output directory
            base_name: Base name for output files
            padding: Padding in seconds
            progress_callback: Optional callback(message, current, total)

        Returns:
            List of created file paths
        """
        output_files = []
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        for i, (start, end) in enumerate(segments, 1):
            padded_start = max(0, start - padding)
            duration = (end + padding) - padded_start

            output_file = str(Path(output_dir) / f"{base_name}_clip_{i:03d}.mp4")

            cmd = [
                self.ffmpeg_path,
                '-ss', str(padded_start),
                '-i', video_path,
                '-t', str(duration),
                '-c:v', 'libx264',
                '-crf', '23',
                '-preset', 'medium',
                '-c:a', 'aac',
                '-b:a', '192k',
                '-y',
                output_file
            ]

            try:
                if progress_callback:
                    progress_callback(f"Exporting clip {i}/{len(segments)}", i, len(segments))

                subprocess.run(cmd, capture_output=True, timeout=None, check=True)
                output_files.append(output_file)

            except Exception as e:
                if progress_callback:
                    progress_callback(f"Error exporting clip {i}: {str(e)}", i, len(segments))

        return output_files

    def merge_clips(
        self,
        clip_paths: List[str],
        output_path: str,
        progress_callback: Optional[Callable[[str], None]] = None
    ) -> bool:
        """Merge multiple video clips into one file"""
        if not clip_paths:
            return False

        # Create concat file
        concat_file = Path(output_path).parent / "concat_list.txt"
        with open(concat_file, 'w') as f:
            for clip in clip_paths:
                f.write(f"file '{Path(clip).absolute()}'\n")

        cmd = [
            self.ffmpeg_path,
            '-f', 'concat',
            '-safe', '0',
            '-i', str(concat_file),
            '-c', 'copy',
            '-y',
            output_path
        ]

        try:
            if progress_callback:
                progress_callback("Merging clips...")

            subprocess.run(cmd, capture_output=True, timeout=None, check=True)

            # Clean up concat file
            concat_file.unlink()

            if progress_callback:
                progress_callback("Clips merged successfully!")

            return True

        except Exception as e:
            if progress_callback:
                progress_callback(f"Error merging clips: {str(e)}")
            return False

    def extract_audio(
        self,
        video_path: str,
        output_path: str,
        progress_callback: Optional[Callable[[str], None]] = None
    ) -> bool:
        """Extract audio from video for Whisper processing"""
        cmd = [
            self.ffmpeg_path,
            '-i', video_path,
            '-vn',
            '-acodec', 'pcm_s16le',
            '-ar', '16000',
            '-ac', '1',
            '-y',
            output_path
        ]

        try:
            if progress_callback:
                progress_callback("Extracting audio...")

            subprocess.run(cmd, capture_output=True, timeout=None, check=True)
            return True

        except Exception as e:
            if progress_callback:
                progress_callback(f"Error extracting audio: {str(e)}")
            return False
