"""Progress window for showing processing status"""

import tkinter as tk
from tkinter import ttk
from typing import Optional


class ProgressWindow:
    """Window showing processing progress"""

    def __init__(self, parent, total_files: int):
        self.window = tk.Toplevel(parent)
        self.window.title("Processing Videos")
        self.window.geometry("600x400")
        self.window.transient(parent)

        self.total_files = total_files
        self.current_file = 0

        self._create_widgets()

        # Center window
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.window.winfo_screenheight() // 2) - (400 // 2)
        self.window.geometry(f"600x400+{x}+{y}")

        # Prevent closing during processing
        self.window.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _create_widgets(self):
        """Create progress window widgets"""
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        ttk.Label(
            main_frame,
            text="Processing Videos",
            font=('Arial', 14, 'bold')
        ).pack(pady=(0, 20))

        # Current file
        self.file_label = ttk.Label(
            main_frame,
            text="Initializing...",
            font=('Arial', 10)
        )
        self.file_label.pack(pady=(0, 10))

        # Overall progress
        ttk.Label(main_frame, text="Overall Progress:").pack(anchor=tk.W)
        self.overall_progress = ttk.Progressbar(
            main_frame,
            mode='determinate',
            length=550
        )
        self.overall_progress.pack(fill=tk.X, pady=(5, 15))

        self.overall_label = ttk.Label(
            main_frame,
            text=f"0 of {self.total_files} files",
            font=('Arial', 9)
        )
        self.overall_label.pack()

        # Current file progress
        ttk.Label(main_frame, text="Current File:").pack(anchor=tk.W, pady=(15, 0))
        self.current_progress = ttk.Progressbar(
            main_frame,
            mode='indeterminate',
            length=550
        )
        self.current_progress.pack(fill=tk.X, pady=(5, 5))
        self.current_progress.start(10)

        # Status
        self.status_label = ttk.Label(
            main_frame,
            text="Starting...",
            font=('Arial', 9),
            foreground='blue'
        )
        self.status_label.pack(pady=(5, 15))

        # Results text
        results_frame = ttk.LabelFrame(main_frame, text="Results", padding="10")
        results_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 10))

        scrollbar = ttk.Scrollbar(results_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.results_text = tk.Text(
            results_frame,
            height=8,
            wrap=tk.WORD,
            yscrollcommand=scrollbar.set,
            font=('Courier', 9)
        )
        self.results_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.results_text.yview)

        # Close button (disabled during processing)
        self.close_button = ttk.Button(
            main_frame,
            text="Close",
            command=self._close,
            state='disabled'
        )
        self.close_button.pack(pady=(10, 0))

    def update_current_file(self, filename: str, file_number: int):
        """Update current file being processed"""
        self.current_file = file_number
        self.file_label.config(text=f"Processing: {filename}")

        # Update overall progress
        progress = (file_number / self.total_files) * 100
        self.overall_progress['value'] = progress
        self.overall_label.config(text=f"{file_number} of {self.total_files} files")

        self.window.update()

    def update_status(self, status: str):
        """Update status message"""
        self.status_label.config(text=status)
        self.window.update()

    def add_result(self, result: str):
        """Add result message to results text"""
        self.results_text.insert(tk.END, result + "\n")
        self.results_text.see(tk.END)
        self.window.update()

    def processing_complete(self):
        """Called when all processing is complete"""
        self.current_progress.stop()
        self.current_progress['mode'] = 'determinate'
        self.current_progress['value'] = 100

        self.overall_progress['value'] = 100
        self.status_label.config(text="Processing complete!", foreground='green')
        self.file_label.config(text="All files processed")

        self.close_button.config(state='normal')
        self.window.protocol("WM_DELETE_WINDOW", self._close)

    def _on_closing(self):
        """Handle window close during processing"""
        # Don't allow closing during processing
        pass

    def _close(self):
        """Close the progress window"""
        self.window.destroy()
