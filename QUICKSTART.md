# StreamCut Pro - Quick Start Guide

Get up and running in 5 minutes!

## Installation (First Time Only)

### Windows
1. Download or clone this repository
2. Double-click `install.bat`
3. Wait for installation to complete

### Mac/Linux
1. Download or clone this repository
2. Open Terminal in the project folder
3. Run: `chmod +x install.sh && ./install.sh`

## Running the App

### Windows
- Double-click `run.bat`
- Or run: `python main.py`

### Mac/Linux
- Run: `./run.sh`
- Or run: `python3 main.py`

## First Time Usage

### Step 1: Add Videos
- Click the drop zone or drag & drop your stream files
- Supported formats: MP4, MKV, AVI, MOV, FLV, WMV, WebM

### Step 2: Choose Processing Mode
- **FFmpeg Only** ⚡ - Fastest (recommended for testing)
- **Whisper AI** 🎯 - Most accurate (requires more time)
- **Hybrid** ⚖️ - Best quality (balanced)

### Step 3: Use a Preset (Optional)
Click one of these for instant configuration:
- **Quick Cut** - Fast & aggressive
- **Safe Cut** - Conservative (keeps more content)
- **Maximum** - Extreme compression

### Step 4: Select Outputs
✅ Merged Video - Single edited file (recommended)
☐ Individual Clips - Separate files for each segment
✅ Timestamp Report - CSV file with cut details
☐ XML Export - For Premiere/Final Cut

### Step 5: Process
1. Click "▶ Process All"
2. Watch the progress window
3. Find your edited videos in the `output` folder!

## What to Expect

### Processing Time
| Original Length | FFmpeg Mode | Hybrid Mode |
|----------------|-------------|-------------|
| 1 hour | ~2-3 min | ~5-8 min |
| 4 hours | ~5-10 min | ~15-25 min |
| 8 hours | ~10-20 min | ~30-45 min |

### Results
- **Original**: 4:23:15 stream
- **Edited**: ~45 minutes (removes 3.5 hours)
- **Files Created**:
  - `my_stream_edited.mp4` (the clean version)
  - `my_stream_timestamps.csv` (what was cut)

## Troubleshooting

### "FFmpeg Not Found"
You need to install FFmpeg first:
- **Windows**: `winget install FFmpeg`
- **Mac**: `brew install ffmpeg`
- **Linux**: `sudo apt install ffmpeg`

### App Won't Start
```bash
# Check Python version (need 3.10+)
python --version

# Reinstall dependencies
pip install -r requirements.txt

# Try running directly
python main.py
```

### Processing Errors
- Make sure the video file isn't corrupted
- Try with a shorter test video first
- Check that you have enough disk space

## Tips & Tricks

### For Best Results
1. **Start with FFmpeg Only mode** for speed
2. **Use "Safe Cut" preset** to avoid cutting too much
3. **Enable Timestamp Report** to see what was removed
4. **Process overnight** for large batches

### Customizing Settings
- **Silence Threshold**: Lower = removes more (try -25dB to -35dB)
- **Min Duration**: Higher = removes less (try 2-5 seconds)
- **Padding**: Keep 0.5-1s before/after speech for natural flow

### Batch Processing Multiple Streams
1. Add all files to queue at once
2. Configure settings once
3. Click "Process All"
4. Go to bed 😴
5. Wake up to edited content! 🎉

## Next Steps

### If It Works Well
- Share with fellow streamers
- Give feedback on what features you want
- Consider supporting the project

### If You Need Help
- Check README.md for detailed docs
- Report issues on GitHub
- Email: support@innovativeautomations.dev

---

**You're all set! Start processing your streams and save hours of editing time.** 🚀
