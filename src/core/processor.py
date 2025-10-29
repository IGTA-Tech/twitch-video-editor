"""Main video processor combining FFmpeg and Whisper"""

import csv
from pathlib import Path
from typing import List, Tuple, Optional, Callable, Dict
from .ffmpeg_handler import FFmpegHandler
from .whisper_handler import WhisperHandler


class VideoProcessor:
    """Main video processor for StreamCut Pro"""

    def __init__(self, config: Dict):
        self.config = config
        self.ffmpeg = FFmpegHandler(config.get('ffmpeg_path', 'ffmpeg'))
        self.whisper = WhisperHandler(config.get('whisper_model', 'base'))
        self.cancelled = False

    def cancel(self):
        """Cancel current processing"""
        self.cancelled = True

    def process_video(
        self,
        video_path: str,
        output_dir: str,
        progress_callback: Optional[Callable[[str], None]] = None
    ) -> Dict:
        """
        Process a single video file

        Args:
            video_path: Path to input video
            output_dir: Output directory
            progress_callback: Optional callback for progress updates

        Returns:
            Dict with processing results
        """
        self.cancelled = False
        results = {
            'success': False,
            'input_file': video_path,
            'output_files': [],
            'original_duration': 0,
            'final_duration': 0,
            'segments_removed': 0,
            'time_saved': 0,
            'error': None
        }

        try:
            # Get video info
            video_info = self.ffmpeg.get_video_info(video_path)
            if video_info and 'format' in video_info:
                results['original_duration'] = float(video_info['format'].get('duration', 0))

            # Get processing mode
            mode = self.config.get('processing_mode', 'ffmpeg')

            # Detect segments to keep
            keep_segments = self._detect_keep_segments(
                video_path,
                mode,
                progress_callback
            )

            if self.cancelled:
                results['error'] = "Processing cancelled by user"
                return results

            if not keep_segments:
                results['error'] = "No segments to keep"
                if progress_callback:
                    progress_callback("Error: No segments detected")
                return results

            # Calculate statistics
            final_duration = sum(end - start for start, end in keep_segments)
            results['final_duration'] = final_duration
            results['time_saved'] = results['original_duration'] - final_duration
            results['segments_removed'] = self._count_removed_segments(
                keep_segments,
                results['original_duration']
            )

            # Create outputs
            base_name = Path(video_path).stem
            output_dir_path = Path(output_dir)
            output_dir_path.mkdir(parents=True, exist_ok=True)

            # Export based on configuration
            if self.config.get('export_merged', True):
                merged_output = str(output_dir_path / f"{base_name}_edited.mp4")
                if self.ffmpeg.cut_video(
                    video_path,
                    keep_segments,
                    merged_output,
                    self.config.get('padding_seconds', 0.5),
                    progress_callback
                ):
                    results['output_files'].append(merged_output)

            if self.cancelled:
                results['error'] = "Processing cancelled by user"
                return results

            if self.config.get('export_clips', False):
                clips_dir = str(output_dir_path / f"{base_name}_clips")
                clip_files = self.ffmpeg.export_clips(
                    video_path,
                    keep_segments,
                    clips_dir,
                    base_name,
                    self.config.get('padding_seconds', 0.5),
                    lambda msg, cur, total: progress_callback(msg) if progress_callback else None
                )
                results['output_files'].extend(clip_files)

            if self.config.get('export_timestamps', True):
                timestamp_file = str(output_dir_path / f"{base_name}_timestamps.csv")
                if self.generate_timestamp_report(
                    keep_segments,
                    timestamp_file,
                    results['original_duration']
                ):
                    results['output_files'].append(timestamp_file)

            if self.config.get('export_xml', False):
                xml_file = str(output_dir_path / f"{base_name}_premiere.xml")
                if self.generate_premiere_xml(
                    keep_segments,
                    xml_file,
                    video_path
                ):
                    results['output_files'].append(xml_file)

            results['success'] = True

            if progress_callback:
                progress_callback(f"✓ Processing complete! Saved {self._format_duration(results['time_saved'])}")

        except Exception as e:
            results['error'] = str(e)
            if progress_callback:
                progress_callback(f"Error: {str(e)}")

        return results

    def _detect_keep_segments(
        self,
        video_path: str,
        mode: str,
        progress_callback: Optional[Callable[[str], None]] = None
    ) -> List[Tuple[float, float]]:
        """Detect segments to keep based on processing mode"""

        if mode == 'ffmpeg':
            # FFmpeg silence detection only
            silence_segments = self.ffmpeg.detect_silence(
                video_path,
                self.config.get('silence_threshold_db', -30),
                self.config.get('min_silence_duration', 2.0),
                progress_callback
            )
            return self._invert_segments(silence_segments, self._get_duration(video_path))

        elif mode == 'whisper':
            # Whisper speech detection only
            return self.whisper.detect_speech_from_video(
                video_path,
                self.ffmpeg,
                self.config.get('min_silence_duration', 2.0),
                progress_callback
            )

        elif mode == 'hybrid':
            # Combine FFmpeg and Whisper
            if progress_callback:
                progress_callback("Using hybrid mode (FFmpeg + Whisper)")

            silence_segments = self.ffmpeg.detect_silence(
                video_path,
                self.config.get('silence_threshold_db', -30),
                self.config.get('min_silence_duration', 2.0),
                progress_callback
            )

            speech_segments = self.whisper.detect_speech_from_video(
                video_path,
                self.ffmpeg,
                self.config.get('min_silence_duration', 2.0),
                progress_callback
            )

            # Keep segments that have speech (from Whisper)
            # but also weren't detected as silence (from FFmpeg)
            return self._merge_segments(speech_segments, silence_segments)

        else:
            return []

    def _get_duration(self, video_path: str) -> float:
        """Get video duration"""
        info = self.ffmpeg.get_video_info(video_path)
        if info and 'format' in info:
            return float(info['format'].get('duration', 0))
        return 0

    def _invert_segments(
        self,
        silence_segments: List[Tuple[float, float]],
        total_duration: float
    ) -> List[Tuple[float, float]]:
        """Convert silence segments to keep segments"""
        if not silence_segments:
            return [(0, total_duration)]

        keep_segments = []
        last_end = 0

        for start, end in sorted(silence_segments):
            if start > last_end:
                keep_segments.append((last_end, start))
            last_end = end

        # Add final segment if needed
        if last_end < total_duration:
            keep_segments.append((last_end, total_duration))

        return keep_segments

    def _merge_segments(
        self,
        speech_segments: List[Tuple[float, float]],
        silence_segments: List[Tuple[float, float]]
    ) -> List[Tuple[float, float]]:
        """Merge speech and silence detection results"""
        # Keep only speech segments that don't overlap with silence
        keep_segments = []

        for speech_start, speech_end in speech_segments:
            # Check if this speech segment overlaps with silence
            overlaps_silence = False
            for silence_start, silence_end in silence_segments:
                if not (speech_end < silence_start or speech_start > silence_end):
                    overlaps_silence = True
                    break

            if not overlaps_silence:
                keep_segments.append((speech_start, speech_end))

        return keep_segments

    def _count_removed_segments(
        self,
        keep_segments: List[Tuple[float, float]],
        total_duration: float
    ) -> int:
        """Count number of segments that were removed"""
        if not keep_segments:
            return 0

        # Number of gaps between kept segments
        return len(keep_segments) - 1

    def generate_timestamp_report(
        self,
        segments: List[Tuple[float, float]],
        output_path: str,
        total_duration: float
    ) -> bool:
        """Generate CSV report with timestamps"""
        try:
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Segment', 'Start', 'End', 'Duration', 'Action'])

                segment_num = 1
                last_end = 0

                for start, end in sorted(segments):
                    # Write cut segment if there's a gap
                    if start > last_end:
                        writer.writerow([
                            f'Cut {segment_num}',
                            self._format_duration(last_end),
                            self._format_duration(start),
                            self._format_duration(start - last_end),
                            'REMOVED'
                        ])
                        segment_num += 1

                    # Write keep segment
                    writer.writerow([
                        f'Clip {segment_num}',
                        self._format_duration(start),
                        self._format_duration(end),
                        self._format_duration(end - start),
                        'KEPT'
                    ])
                    segment_num += 1
                    last_end = end

                # Final cut if needed
                if last_end < total_duration:
                    writer.writerow([
                        f'Cut {segment_num}',
                        self._format_duration(last_end),
                        self._format_duration(total_duration),
                        self._format_duration(total_duration - last_end),
                        'REMOVED'
                    ])

            return True

        except Exception as e:
            print(f"Error generating timestamp report: {e}")
            return False

    def generate_premiere_xml(
        self,
        segments: List[Tuple[float, float]],
        output_path: str,
        video_path: str
    ) -> bool:
        """Generate XML markers for Adobe Premiere Pro"""
        try:
            xml_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<fcpxml version="1.8">
    <resources>
        <asset id="asset1" src="file://{video_path}" hasVideo="1" hasAudio="1"/>
    </resources>
    <library>
        <event name="StreamCut Markers">
            <project name="Edited Stream">
                <sequence>
                    <spine>
'''
            for i, (start, end) in enumerate(segments, 1):
                duration = end - start
                xml_content += f'''                        <asset-clip ref="asset1" offset="{start}s" duration="{duration}s" name="Clip {i}"/>
'''

            xml_content += '''                    </spine>
                </sequence>
            </project>
        </event>
    </library>
</fcpxml>
'''
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(xml_content)

            return True

        except Exception as e:
            print(f"Error generating XML: {e}")
            return False

    @staticmethod
    def _format_duration(seconds: float) -> str:
        """Format seconds as HH:MM:SS"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
