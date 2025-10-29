"""Main GUI window for StreamCut Pro"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from typing import List, Optional
import threading

from ..utils.config import Config
from ..utils.file_utils import is_video_file, check_ffmpeg_installed, format_duration, get_video_duration
from ..core.processor import VideoProcessor
from .progress_window import ProgressWindow


class MainWindow:
    """Main application window"""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.config = Config()
        self.file_queue: List[str] = []
        self.processing = False
        self.processor: Optional[VideoProcessor] = None

        self._setup_window()
        self._create_widgets()
        self._check_dependencies()
        self._apply_config()

    def _setup_window(self):
        """Setup main window"""
        self.root.title("StreamCut Pro - Beta v0.1")
        self.root.geometry(self.config.get('window_geometry', '900x750'))

        # Set minimum size
        self.root.minsize(800, 600)

        # Configure grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _create_widgets(self):
        """Create all GUI widgets"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.columnconfigure(0, weight=1)

        # Title
        title_label = ttk.Label(
            main_frame,
            text="StreamCut Pro",
            font=('Arial', 20, 'bold')
        )
        title_label.grid(row=0, column=0, pady=(0, 5))

        subtitle_label = ttk.Label(
            main_frame,
            text="Automated Video Editor for Streamers",
            font=('Arial', 10)
        )
        subtitle_label.grid(row=1, column=0, pady=(0, 15))

        # Drop zone
        self._create_drop_zone(main_frame, row=2)

        # File queue
        self._create_file_queue(main_frame, row=3)

        # Processing mode
        self._create_processing_mode(main_frame, row=4)

        # Settings
        self._create_settings(main_frame, row=5)

        # Export options
        self._create_export_options(main_frame, row=6)

        # Output folder
        self._create_output_folder(main_frame, row=7)

        # Presets and process buttons
        self._create_action_buttons(main_frame, row=8)

        # Status bar
        self._create_status_bar(main_frame, row=9)

    def _create_drop_zone(self, parent, row):
        """Create drag-and-drop zone"""
        drop_frame = ttk.LabelFrame(parent, text="Add Video Files", padding="20")
        drop_frame.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        drop_label = ttk.Label(
            drop_frame,
            text="📁 Click to Browse or Drag & Drop Video Files Here",
            font=('Arial', 11),
            cursor="hand2"
        )
        drop_label.pack(pady=30)
        drop_label.bind('<Button-1>', lambda e: self._browse_files())

        # Enable drag and drop (basic implementation)
        drop_frame.bind('<Button-1>', lambda e: self._browse_files())

    def _create_file_queue(self, parent, row):
        """Create file queue list"""
        queue_frame = ttk.LabelFrame(parent, text="File Queue", padding="10")
        queue_frame.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        queue_frame.columnconfigure(0, weight=1)

        # Listbox with scrollbar
        list_frame = ttk.Frame(queue_frame)
        list_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        list_frame.columnconfigure(0, weight=1)

        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        self.queue_listbox = tk.Listbox(
            list_frame,
            height=5,
            yscrollcommand=scrollbar.set,
            font=('Arial', 9)
        )
        self.queue_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E))
        scrollbar.config(command=self.queue_listbox.yview)

        # Buttons
        button_frame = ttk.Frame(queue_frame)
        button_frame.grid(row=1, column=0, pady=(5, 0))

        ttk.Button(
            button_frame,
            text="Add Files",
            command=self._browse_files
        ).pack(side=tk.LEFT, padx=2)

        ttk.Button(
            button_frame,
            text="Remove Selected",
            command=self._remove_selected
        ).pack(side=tk.LEFT, padx=2)

        ttk.Button(
            button_frame,
            text="Clear All",
            command=self._clear_queue
        ).pack(side=tk.LEFT, padx=2)

    def _create_processing_mode(self, parent, row):
        """Create processing mode selector"""
        mode_frame = ttk.LabelFrame(parent, text="Processing Mode", padding="10")
        mode_frame.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        self.mode_var = tk.StringVar(value=self.config.get('processing_mode', 'ffmpeg'))

        modes = [
            ('ffmpeg', 'FFmpeg Only (Fastest - 5-10 min for 4hr video)'),
            ('whisper', 'Whisper AI (Most Accurate - 20-30 min)'),
            ('hybrid', 'Hybrid (Best Quality - 10-20 min)')
        ]

        for i, (value, text) in enumerate(modes):
            ttk.Radiobutton(
                mode_frame,
                text=text,
                variable=self.mode_var,
                value=value
            ).grid(row=0, column=i, padx=10, sticky=tk.W)

    def _create_settings(self, parent, row):
        """Create settings controls"""
        settings_frame = ttk.LabelFrame(parent, text="Settings", padding="10")
        settings_frame.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        settings_frame.columnconfigure(1, weight=1)

        # Silence threshold
        ttk.Label(settings_frame, text="Silence Threshold:").grid(
            row=0, column=0, sticky=tk.W, padx=(0, 10)
        )
        self.threshold_var = tk.IntVar(value=int(self.config.get('silence_threshold_db', -30)))
        threshold_frame = ttk.Frame(settings_frame)
        threshold_frame.grid(row=0, column=1, sticky=(tk.W, tk.E))
        ttk.Scale(
            threshold_frame,
            from_=-50,
            to=-10,
            variable=self.threshold_var,
            orient=tk.HORIZONTAL
        ).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Label(
            threshold_frame,
            textvariable=self.threshold_var,
            width=5
        ).pack(side=tk.LEFT, padx=(5, 0))
        ttk.Label(threshold_frame, text="dB").pack(side=tk.LEFT)

        # Min duration
        ttk.Label(settings_frame, text="Min Silence Duration:").grid(
            row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(5, 0)
        )
        self.duration_var = tk.DoubleVar(value=self.config.get('min_silence_duration', 2.0))
        duration_frame = ttk.Frame(settings_frame)
        duration_frame.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=(5, 0))
        ttk.Scale(
            duration_frame,
            from_=0.5,
            to=10.0,
            variable=self.duration_var,
            orient=tk.HORIZONTAL
        ).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Label(
            duration_frame,
            textvariable=self.duration_var,
            width=5
        ).pack(side=tk.LEFT, padx=(5, 0))
        ttk.Label(duration_frame, text="sec").pack(side=tk.LEFT)

        # Padding
        ttk.Label(settings_frame, text="Padding:").grid(
            row=2, column=0, sticky=tk.W, padx=(0, 10), pady=(5, 0)
        )
        self.padding_var = tk.DoubleVar(value=self.config.get('padding_seconds', 0.5))
        padding_frame = ttk.Frame(settings_frame)
        padding_frame.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=(5, 0))
        ttk.Scale(
            padding_frame,
            from_=0.0,
            to=3.0,
            variable=self.padding_var,
            orient=tk.HORIZONTAL
        ).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Label(
            padding_frame,
            textvariable=self.padding_var,
            width=5
        ).pack(side=tk.LEFT, padx=(5, 0))
        ttk.Label(padding_frame, text="sec").pack(side=tk.LEFT)

    def _create_export_options(self, parent, row):
        """Create export options"""
        export_frame = ttk.LabelFrame(parent, text="Export Options", padding="10")
        export_frame.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        self.export_merged_var = tk.BooleanVar(value=self.config.get('export_merged', True))
        self.export_clips_var = tk.BooleanVar(value=self.config.get('export_clips', False))
        self.export_timestamps_var = tk.BooleanVar(value=self.config.get('export_timestamps', True))
        self.export_xml_var = tk.BooleanVar(value=self.config.get('export_xml', False))

        ttk.Checkbutton(
            export_frame,
            text="Merged Video (Single File)",
            variable=self.export_merged_var
        ).grid(row=0, column=0, sticky=tk.W, padx=10)

        ttk.Checkbutton(
            export_frame,
            text="Individual Clips",
            variable=self.export_clips_var
        ).grid(row=0, column=1, sticky=tk.W, padx=10)

        ttk.Checkbutton(
            export_frame,
            text="Timestamp Report (CSV)",
            variable=self.export_timestamps_var
        ).grid(row=1, column=0, sticky=tk.W, padx=10, pady=(5, 0))

        ttk.Checkbutton(
            export_frame,
            text="XML for Premiere/Final Cut",
            variable=self.export_xml_var
        ).grid(row=1, column=1, sticky=tk.W, padx=10, pady=(5, 0))

    def _create_output_folder(self, parent, row):
        """Create output folder selector"""
        folder_frame = ttk.Frame(parent)
        folder_frame.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        folder_frame.columnconfigure(1, weight=1)

        ttk.Label(folder_frame, text="Output Folder:").grid(row=0, column=0, padx=(0, 10))

        self.output_folder_var = tk.StringVar(value=self.config.get('output_folder', './output'))
        output_entry = ttk.Entry(folder_frame, textvariable=self.output_folder_var)
        output_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))

        ttk.Button(
            folder_frame,
            text="Browse...",
            command=self._browse_output_folder
        ).grid(row=0, column=2)

    def _create_action_buttons(self, parent, row):
        """Create preset and action buttons"""
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=row, column=0, pady=15)

        # Presets
        ttk.Label(button_frame, text="Quick Presets:").pack(side=tk.LEFT, padx=(0, 10))

        ttk.Button(
            button_frame,
            text="Quick Cut",
            command=lambda: self._apply_preset('quick')
        ).pack(side=tk.LEFT, padx=2)

        ttk.Button(
            button_frame,
            text="Safe Cut",
            command=lambda: self._apply_preset('safe')
        ).pack(side=tk.LEFT, padx=2)

        ttk.Button(
            button_frame,
            text="Maximum",
            command=lambda: self._apply_preset('maximum')
        ).pack(side=tk.LEFT, padx=2)

        # Separator
        ttk.Separator(button_frame, orient=tk.VERTICAL).pack(
            side=tk.LEFT, fill=tk.Y, padx=15
        )

        # Process button
        self.process_button = ttk.Button(
            button_frame,
            text="▶ Process All",
            command=self._process_all,
            style='Accent.TButton'
        )
        self.process_button.pack(side=tk.LEFT, padx=2)

    def _create_status_bar(self, parent, row):
        """Create status bar"""
        self.status_var = tk.StringVar(value="Ready")

        status_frame = ttk.Frame(parent)
        status_frame.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=(10, 0))

        ttk.Label(
            status_frame,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W
        ).pack(fill=tk.X)

    def _check_dependencies(self):
        """Check if required dependencies are installed"""
        ffmpeg_installed, version = check_ffmpeg_installed()
        if not ffmpeg_installed:
            messagebox.showwarning(
                "FFmpeg Not Found",
                "FFmpeg is not installed or not in PATH.\n\n"
                "Please install FFmpeg to use this application:\n"
                "- Windows: Download from ffmpeg.org\n"
                "- Mac: brew install ffmpeg\n"
                "- Linux: sudo apt install ffmpeg"
            )
            self.process_button.config(state='disabled')
        else:
            self.status_var.set(f"Ready - {version}")

    def _apply_config(self):
        """Apply saved configuration"""
        self.mode_var.set(self.config.get('processing_mode', 'ffmpeg'))
        self.threshold_var.set(int(self.config.get('silence_threshold_db', -30)))
        self.duration_var.set(self.config.get('min_silence_duration', 2.0))
        self.padding_var.set(self.config.get('padding_seconds', 0.5))

    def _browse_files(self):
        """Browse for video files"""
        files = filedialog.askopenfilenames(
            title="Select Video Files",
            filetypes=[
                ("Video Files", "*.mp4 *.mkv *.avi *.mov *.flv *.wmv *.webm *.m4v"),
                ("All Files", "*.*")
            ]
        )

        for file in files:
            if file not in self.file_queue and is_video_file(file):
                self.file_queue.append(file)
                filename = Path(file).name
                self.queue_listbox.insert(tk.END, filename)

        self.status_var.set(f"{len(self.file_queue)} file(s) in queue")

    def _remove_selected(self):
        """Remove selected files from queue"""
        selection = self.queue_listbox.curselection()
        if selection:
            index = selection[0]
            self.file_queue.pop(index)
            self.queue_listbox.delete(index)
            self.status_var.set(f"{len(self.file_queue)} file(s) in queue")

    def _clear_queue(self):
        """Clear all files from queue"""
        self.file_queue.clear()
        self.queue_listbox.delete(0, tk.END)
        self.status_var.set("Queue cleared")

    def _browse_output_folder(self):
        """Browse for output folder"""
        folder = filedialog.askdirectory(title="Select Output Folder")
        if folder:
            self.output_folder_var.set(folder)

    def _apply_preset(self, preset_name: str):
        """Apply preset configuration"""
        presets = {
            'quick': {
                'threshold_db': -25,
                'min_duration': 3.0,
                'padding': 0.3,
                'mode': 'ffmpeg'
            },
            'safe': {
                'threshold_db': -35,
                'min_duration': 1.5,
                'padding': 1.0,
                'mode': 'hybrid'
            },
            'maximum': {
                'threshold_db': -20,
                'min_duration': 5.0,
                'padding': 0.1,
                'mode': 'ffmpeg'
            }
        }

        preset = presets.get(preset_name, {})
        if preset:
            self.threshold_var.set(preset.get('threshold_db', -30))
            self.duration_var.set(preset.get('min_duration', 2.0))
            self.padding_var.set(preset.get('padding', 0.5))
            self.mode_var.set(preset.get('mode', 'ffmpeg'))
            self.status_var.set(f"Applied {preset_name.title()} preset")

    def _process_all(self):
        """Process all files in queue"""
        if not self.file_queue:
            messagebox.showwarning("No Files", "Please add video files to the queue first.")
            return

        if self.processing:
            messagebox.showinfo("Processing", "Already processing files.")
            return

        # Save current settings to config
        self.config.update({
            'processing_mode': self.mode_var.get(),
            'silence_threshold_db': float(self.threshold_var.get()),
            'min_silence_duration': self.duration_var.get(),
            'padding_seconds': self.padding_var.get(),
            'export_merged': self.export_merged_var.get(),
            'export_clips': self.export_clips_var.get(),
            'export_timestamps': self.export_timestamps_var.get(),
            'export_xml': self.export_xml_var.get(),
            'output_folder': self.output_folder_var.get()
        })
        self.config.save()

        # Start processing in background thread
        self.processing = True
        self.process_button.config(state='disabled')

        progress_window = ProgressWindow(self.root, len(self.file_queue))

        def process_thread():
            try:
                self.processor = VideoProcessor(self.config.config)

                for i, video_file in enumerate(self.file_queue, 1):
                    if not self.processing:
                        break

                    filename = Path(video_file).name
                    progress_window.update_current_file(filename, i)

                    result = self.processor.process_video(
                        video_file,
                        self.output_folder_var.get(),
                        progress_callback=progress_window.update_status
                    )

                    if result['success']:
                        saved_time = format_duration(result.get('time_saved', 0))
                        progress_window.add_result(
                            f"✓ {filename}: Saved {saved_time}"
                        )
                    else:
                        error = result.get('error', 'Unknown error')
                        progress_window.add_result(f"✗ {filename}: {error}")

                progress_window.processing_complete()

            except Exception as e:
                progress_window.add_result(f"Error: {str(e)}")
                progress_window.processing_complete()

            finally:
                self.processing = False
                self.root.after(0, lambda: self.process_button.config(state='normal'))

        thread = threading.Thread(target=process_thread, daemon=True)
        thread.start()

    def _on_closing(self):
        """Handle window close event"""
        if self.processing:
            if messagebox.askokcancel("Quit", "Processing in progress. Cancel and quit?"):
                self.processing = False
                if self.processor:
                    self.processor.cancel()
                self.root.destroy()
        else:
            # Save window geometry
            self.config.set('window_geometry', self.root.geometry())
            self.config.save()
            self.root.destroy()
