"""Whisper handler for AI-powered speech detection"""

import os
from pathlib import Path
from typing import List, Tuple, Optional, Callable, Dict
import tempfile

class WhisperHandler:
    """Handles Whisper AI speech detection"""

    def __init__(self, model_name: str = "base"):
        self.model_name = model_name
        self.model = None
        self._whisper_available = None

    def is_whisper_available(self) -> bool:
        """Check if Whisper is installed and available"""
        if self._whisper_available is not None:
            return self._whisper_available

        try:
            import whisper
            self._whisper_available = True
            return True
        except ImportError:
            self._whisper_available = False
            return False

    def load_model(self, progress_callback: Optional[Callable[[str], None]] = None):
        """Load Whisper model"""
        if not self.is_whisper_available():
            if progress_callback:
                progress_callback("Whisper not installed. Install with: pip install openai-whisper")
            return False

        try:
            import whisper

            if progress_callback:
                progress_callback(f"Loading Whisper {self.model_name} model...")

            self.model = whisper.load_model(self.model_name)

            if progress_callback:
                progress_callback("Whisper model loaded successfully")

            return True

        except Exception as e:
            if progress_callback:
                progress_callback(f"Error loading Whisper model: {str(e)}")
            return False

    def transcribe_audio(
        self,
        audio_path: str,
        progress_callback: Optional[Callable[[str], None]] = None
    ) -> Optional[Dict]:
        """
        Transcribe audio file using Whisper

        Args:
            audio_path: Path to audio file
            progress_callback: Optional callback for progress updates

        Returns:
            Transcription result dict or None if error
        """
        if not self.is_whisper_available():
            if progress_callback:
                progress_callback("Whisper not available")
            return None

        if self.model is None:
            if not self.load_model(progress_callback):
                return None

        try:
            if progress_callback:
                progress_callback("Transcribing audio with Whisper AI...")

            result = self.model.transcribe(
                audio_path,
                verbose=False,
                word_timestamps=True
            )

            if progress_callback:
                progress_callback("Transcription complete")

            return result

        except Exception as e:
            if progress_callback:
                progress_callback(f"Error transcribing audio: {str(e)}")
            return None

    def get_speech_segments(
        self,
        transcription: Dict,
        min_gap: float = 2.0
    ) -> List[Tuple[float, float]]:
        """
        Extract speech segments from transcription

        Args:
            transcription: Whisper transcription result
            min_gap: Minimum gap between segments to split them

        Returns:
            List of (start, end) tuples for speech segments
        """
        if not transcription or 'segments' not in transcription:
            return []

        segments = []
        current_start = None
        current_end = None

        for segment in transcription['segments']:
            start = segment['start']
            end = segment['end']

            if current_start is None:
                current_start = start
                current_end = end
            else:
                # If gap is small, merge segments
                if start - current_end <= min_gap:
                    current_end = end
                else:
                    # Save current segment and start new one
                    segments.append((current_start, current_end))
                    current_start = start
                    current_end = end

        # Don't forget the last segment
        if current_start is not None:
            segments.append((current_start, current_end))

        return segments

    def detect_speech_from_video(
        self,
        video_path: str,
        ffmpeg_handler,
        min_gap: float = 2.0,
        progress_callback: Optional[Callable[[str], None]] = None
    ) -> List[Tuple[float, float]]:
        """
        Detect speech segments from video using Whisper

        Args:
            video_path: Path to video file
            ffmpeg_handler: FFmpegHandler instance for audio extraction
            min_gap: Minimum gap between speech segments
            progress_callback: Optional callback for progress updates

        Returns:
            List of (start, end) tuples for speech segments
        """
        # Create temporary audio file
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_audio:
            temp_audio_path = temp_audio.name

        try:
            # Extract audio from video
            if not ffmpeg_handler.extract_audio(video_path, temp_audio_path, progress_callback):
                return []

            # Transcribe audio
            transcription = self.transcribe_audio(temp_audio_path, progress_callback)
            if not transcription:
                return []

            # Extract speech segments
            segments = self.get_speech_segments(transcription, min_gap)

            if progress_callback:
                progress_callback(f"Found {len(segments)} speech segments")

            return segments

        finally:
            # Clean up temporary file
            if os.path.exists(temp_audio_path):
                try:
                    os.unlink(temp_audio_path)
                except:
                    pass

    def get_transcript_text(self, transcription: Dict) -> str:
        """Get full transcript text from transcription result"""
        if not transcription or 'text' not in transcription:
            return ""
        return transcription['text'].strip()

    def export_transcript(
        self,
        transcription: Dict,
        output_path: str,
        format: str = 'txt'
    ) -> bool:
        """
        Export transcription to file

        Args:
            transcription: Whisper transcription result
            output_path: Output file path
            format: Output format ('txt', 'srt', 'vtt')

        Returns:
            True if successful
        """
        try:
            if format == 'txt':
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(self.get_transcript_text(transcription))
                return True

            elif format == 'srt' and 'segments' in transcription:
                with open(output_path, 'w', encoding='utf-8') as f:
                    for i, segment in enumerate(transcription['segments'], 1):
                        start = self._format_timestamp(segment['start'])
                        end = self._format_timestamp(segment['end'])
                        text = segment['text'].strip()

                        f.write(f"{i}\n")
                        f.write(f"{start} --> {end}\n")
                        f.write(f"{text}\n\n")
                return True

            return False

        except Exception as e:
            print(f"Error exporting transcript: {e}")
            return False

    @staticmethod
    def _format_timestamp(seconds: float) -> str:
        """Format seconds to SRT timestamp format (HH:MM:SS,mmm)"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
