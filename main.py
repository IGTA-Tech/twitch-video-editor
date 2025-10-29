#!/usr/bin/env python3
"""
StreamCut Pro - Automated Video Editor for Twitch Streamers
Main entry point
"""

import tkinter as tk
from tkinter import ttk
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.gui.main_window import MainWindow


def main():
    """Main application entry point"""
    root = tk.Tk()

    # Set style
    style = ttk.Style()
    style.theme_use('clam')  # Modern theme

    # Create main window
    app = MainWindow(root)

    # Start main loop
    root.mainloop()


if __name__ == "__main__":
    main()
