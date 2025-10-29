# StreamCut Pro - Automated Video Editor for Twitch Streamers

**Turn your 8-hour stream into 45 minutes of content in just 10 minutes - no editing skills required.**

StreamCut Pro is a desktop application that automatically removes dead air, silent sections, and AFK moments from your Twitch VODs, saving you hours of manual editing.

## 🌟 Key Features

- **⚡ Blazing Fast** - Process 4-hour streams in 5-15 minutes
- **🤖 AI-Powered** - FFmpeg + OpenAI Whisper for smart detection
- **📦 Batch Processing** - Drop 50 streams, process overnight
- **💾 Unlimited Files** - No file size limits (14+ hour streams supported)
- **🎯 Smart Presets** - Quick Cut, Safe Cut, Maximum compression modes
- **📤 Multiple Exports** - Merged video, individual clips, timestamps, XML
- **🔒 100% Private** - Everything runs locally on your computer
- **💰 No Subscription** - One-time setup, use forever

## 🎮 Built for Streamers

Unlike general video editors, StreamCut Pro is specifically designed for streamers who need to:
- Process hours of content regularly
- Remove loading screens, AFK breaks, and dead air
- Create highlight reels and YouTube content
- Save time and money on editing

## 🚀 Quick Start

### Installation

#### Windows
```bash
# 1. Download or clone this repository
git clone https://github.com/IGTA-Tech/streamcut-pro.git
cd streamcut-pro

# 2. Run installation script
install.bat

# 3. Launch the app
run.bat
```

#### Mac/Linux
```bash
# 1. Download or clone this repository
git clone https://github.com/IGTA-Tech/streamcut-pro.git
cd streamcut-pro

# 2. Run installation script
chmod +x install.sh
./install.sh

# 3. Launch the app
./run.sh
```

### Manual Installation
```bash
# Install Python dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

## 📋 Requirements

### Required
- **Python 3.10+** - [Download](https://python.org)
- **FFmpeg** - [Download](https://ffmpeg.org)

### Optional (for AI features)
- **OpenAI Whisper** - Installed automatically with requirements.txt
- **CUDA/GPU** - For faster Whisper processing (optional)

### System Requirements
- **Minimum**: Dual-core CPU, 4GB RAM, 10GB free space
- **Recommended**: Quad-core CPU, 8GB+ RAM, SSD storage
- **OS**: Windows 10+, macOS 10.14+, Ubuntu 18.04+

## 🎯 How to Use

1. **Add Videos** - Drag & drop your stream files or click to browse
2. **Choose Mode**:
   - FFmpeg Only (Fastest - 5-10 min)
   - Whisper AI (Most Accurate - 20-30 min)
   - Hybrid (Best Quality - 10-20 min)
3. **Adjust Settings** - Or use Quick Presets
4. **Select Exports** - Merged video, clips, timestamps, XML
5. **Click Process** - Sit back and let it work!

### Processing Modes Explained

| Mode | Speed | Accuracy | Best For |
|------|-------|----------|----------|
| **FFmpeg Only** | ⚡ Fastest | Good | Clean audio with clear pauses |
| **Whisper AI** | 🐌 Slower | Excellent | Complex audio, multiple speakers |
| **Hybrid** | ⚖️ Balanced | Best | Maximum quality (recommended) |

## 📤 Export Options

- **Merged Video** - Single edited file with all silent parts removed
- **Individual Clips** - Each speaking segment as separate file
- **Timestamp CSV** - Report showing what was kept/removed
- **XML Export** - Import into Premiere Pro, Final Cut Pro, DaVinci Resolve

## ⚙️ Advanced Features

### Smart Presets
- **Quick Cut**: Aggressive removal (3s+ silence, -25dB threshold)
- **Safe Cut**: Conservative (1.5s+ silence, -35dB threshold)
- **Maximum**: Extreme compression (5s+ silence, -20dB threshold)

### Custom Settings
- **Silence Threshold** - How quiet is "silence" (-50dB to -10dB)
- **Min Duration** - Minimum silence length to remove (0.5s to 10s)
- **Padding** - Keep X seconds before/after speech (0s to 3s)

### Batch Processing
1. Add multiple files to queue
2. Configure settings once
3. Click "Process All"
4. Results saved to separate folders

## 🏆 Why StreamCut Pro?

### vs. TimeBolt ($347)
✅ $200+ cheaper
✅ Batch processing
✅ Whisper AI integration
✅ More export options

### vs. Descript ($192/year)
✅ One-time purchase
✅ Local processing (no upload wait)
✅ No file size limits
✅ Built for streamers

### vs. Cloud Tools
✅ Handles 14+ hour files
✅ No upload time
✅ 100% private
✅ Works offline

## 📁 Project Structure

```
streamcut-pro/
├── main.py                 # Main application entry
├── requirements.txt        # Python dependencies
├── install.sh/.bat        # Installation scripts
├── run.sh/.bat            # Launch scripts
├── src/
│   ├── core/              # Processing engine
│   │   ├── ffmpeg_handler.py    # FFmpeg operations
│   │   ├── whisper_handler.py   # Whisper AI integration
│   │   └── processor.py         # Main processor
│   ├── gui/               # User interface
│   │   ├── main_window.py       # Main GUI
│   │   └── progress_window.py   # Progress tracking
│   └── utils/             # Utilities
│       ├── config.py            # Configuration
│       └── file_utils.py        # File operations
├── config/                # Configuration files
├── output/                # Processed videos (auto-created)
└── logs/                  # Application logs
```

## 🛠️ Troubleshooting

### FFmpeg Not Found
**Windows**:
```bash
# Install with winget
winget install FFmpeg

# Or download from https://ffmpeg.org
```

**Mac**:
```bash
brew install ffmpeg
```

**Linux**:
```bash
sudo apt install ffmpeg
```

### Whisper Installation Issues
```bash
# If Whisper fails to install
pip install --upgrade pip
pip install openai-whisper --no-cache-dir

# For GPU support
pip install openai-whisper[cuda]
```

### Slow Processing
- Use "FFmpeg Only" mode for faster processing
- Close other applications
- Process during downtime (overnight)
- Consider GPU acceleration for Whisper

### Out of Memory
- Process files one at a time
- Use "FFmpeg Only" mode
- Reduce video quality settings
- Add more RAM or use smaller chunks

## 🤝 Contributing

This is an MVP beta version. Contributions, bug reports, and feature requests are welcome!

## 📄 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

- FFmpeg - Video processing engine
- OpenAI Whisper - Speech recognition
- Python tkinter - GUI framework

## 📞 Support

For issues, questions, or feature requests:
- GitHub Issues: [Report here](https://github.com/IGTA-Tech/streamcut-pro/issues)
- Email: support@innovativeautomations.dev

---

**Made with ❤️ for the streaming community**

*Stop paying $200/year to edit streams. Own it once, use it forever.*
