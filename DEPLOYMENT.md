# StreamCut Pro - Deployment Guide

How to distribute StreamCut Pro to beta testers and customers.

## Table of Contents
1. [For Beta Testing](#for-beta-testing)
2. [Creating Installers](#creating-installers)
3. [Distribution Methods](#distribution-methods)
4. [Licensing](#licensing)

---

## For Beta Testing

### Method 1: GitHub Repository (Recommended)
```bash
# 1. Create GitHub repo
gh repo create streamcut-pro --public --source=. --remote=origin

# 2. Push code
git add .
git commit -m "Initial release - StreamCut Pro v0.1 Beta"
git push -u origin main

# 3. Share repo link with beta testers
# They clone and run install.sh/.bat
```

### Method 2: ZIP Distribution
```bash
# 1. Create clean distribution ZIP
zip -r streamcut-pro-v0.1-beta.zip . \
  -x "*.git*" "*.pyc" "__pycache__/*" "output/*" "*.log"

# 2. Upload to Dropbox/Google Drive
# 3. Share download link

# Beta testers:
# - Extract ZIP
# - Run install.bat (Windows) or ./install.sh (Mac/Linux)
# - Run the app with run.bat or ./run.sh
```

### Beta Tester Instructions
Send this to your beta testers:

```
# StreamCut Pro Beta - Installation

1. Download: [LINK]
2. Extract the ZIP file
3. Installation:
   - Windows: Double-click install.bat
   - Mac/Linux: Open Terminal, run: chmod +x install.sh && ./install.sh
4. Run:
   - Windows: Double-click run.bat
   - Mac/Linux: Run: ./run.sh
5. Test with a short stream first (10-30 min)
6. Report any bugs or feedback

Requirements:
- Python 3.10+ (https://python.org)
- FFmpeg (https://ffmpeg.org)
```

---

## Creating Installers

### Option 1: PyInstaller (Standalone Executable)

#### Install PyInstaller
```bash
pip install pyinstaller
```

#### Build Windows EXE
```bash
pyinstaller --name StreamCutPro \
  --onefile \
  --windowed \
  --icon=assets/icon.ico \
  --add-data "src;src" \
  --add-data "config;config" \
  main.py

# Output: dist/StreamCutPro.exe
```

#### Build Mac App
```bash
pyinstaller --name StreamCutPro \
  --onefile \
  --windowed \
  --icon=assets/icon.icns \
  --add-data "src:src" \
  --add-data "config:config" \
  --osx-bundle-identifier com.innovativeautomations.streamcutpro \
  main.py

# Output: dist/StreamCutPro.app
```

#### Build Linux Binary
```bash
pyinstaller --name StreamCutPro \
  --onefile \
  --add-data "src:src" \
  --add-data "config:config" \
  main.py

# Output: dist/StreamCutPro
```

**Note**: FFmpeg must still be installed separately by users.

### Option 2: Create Installer Packages

#### Windows Installer (Inno Setup)
1. Download Inno Setup: https://jrsoftware.org/isinfo.php
2. Create `installer.iss`:

```iss
[Setup]
AppName=StreamCut Pro
AppVersion=0.1.0
DefaultDirName={pf}\StreamCut Pro
OutputDir=dist
OutputBaseFilename=StreamCutPro-Setup-v0.1
Compression=lzma2
SolidCompression=yes

[Files]
Source: "dist\StreamCutPro.exe"; DestDir: "{app}"
Source: "README.md"; DestDir: "{app}"

[Icons]
Name: "{commondesktop}\StreamCut Pro"; Filename: "{app}\StreamCutPro.exe"
Name: "{group}\StreamCut Pro"; Filename: "{app}\StreamCutPro.exe"
```

3. Compile to create setup.exe

#### Mac DMG
```bash
# Using create-dmg
brew install create-dmg

create-dmg \
  --volname "StreamCut Pro" \
  --window-pos 200 120 \
  --window-size 600 400 \
  --icon-size 100 \
  --app-drop-link 425 120 \
  "StreamCutPro-v0.1.dmg" \
  "dist/StreamCutPro.app"
```

---

## Distribution Methods

### Free Beta Distribution

#### GitHub Releases
```bash
# 1. Create a release
git tag v0.1-beta
git push origin v0.1-beta

# 2. Upload binaries via GitHub UI:
# - StreamCutPro-Windows.exe
# - StreamCutPro-Mac.dmg
# - StreamCutPro-Linux.tar.gz
# - Source code ZIP

# 3. Mark as "Pre-release"
```

#### Direct Download
- Host on your own server
- Use Dropbox/Google Drive
- Use file hosting (WeTransfer, etc.)

### Paid Distribution

#### Gumroad (Recommended)
1. Create account at gumroad.com
2. Upload your executable/ZIP
3. Set price ($79-129)
4. Gumroad handles:
   - Payment processing (5% + $0.25 fee)
   - Download delivery
   - License key generation
   - Updates

#### Lemon Squeezy
- Similar to Gumroad
- Better for EU/VAT
- 5% + payment fees

#### Paddle
- Merchant of record
- Handles all taxes/VAT
- Higher fees (~10%)
- Good for worldwide sales

### Self-Hosted
```bash
# Use a simple PHP/Node.js payment system
# Stripe for payments
# SendOwl/FetchApp for delivery
```

---

## Licensing

### Option 1: Free Beta (MVP Phase)
- No license checks
- Just distribute freely
- Collect testimonials and feedback

### Option 2: Simple License Key System

Create `src/utils/license.py`:
```python
import hashlib
import platform

def generate_license_key(email: str, secret: str = "your-secret") -> str:
    """Generate license key from email"""
    data = f"{email}{secret}"
    return hashlib.sha256(data.encode()).hexdigest()[:16].upper()

def verify_license_key(email: str, key: str, secret: str = "your-secret") -> bool:
    """Verify license key"""
    expected = generate_license_key(email, secret)
    return key.upper() == expected
```

Update `main.py`:
```python
from src.utils.license import verify_license_key

# On startup, check license
email = config.get('license_email')
key = config.get('license_key')

if not verify_license_key(email, key):
    show_license_dialog()
```

### Option 3: Online License Validation
- Use Gumroad's License API
- Use Keygen.sh
- Use LicenseSpring

---

## GitHub Distribution Workflow

### Complete Launch Steps

```bash
# 1. Finalize code
git add .
git commit -m "v0.1 Beta Release - Ready for distribution"

# 2. Create release
git tag -a v0.1-beta -m "Beta release"
git push origin main
git push origin v0.1-beta

# 3. Build executables (if using PyInstaller)
pyinstaller streamcut-pro.spec

# 4. Create GitHub release
gh release create v0.1-beta \
  --title "StreamCut Pro v0.1 Beta" \
  --notes "Initial beta release. See README.md for details." \
  --prerelease \
  dist/StreamCutPro-Windows.exe#Windows \
  dist/StreamCutPro-Mac.dmg#Mac \
  dist/StreamCutPro-Linux.tar.gz#Linux

# 5. Share release URL
echo "https://github.com/IGTA-Tech/streamcut-pro/releases/tag/v0.1-beta"
```

---

## Landing Page (Optional)

Create simple HTML page:

```html
<!DOCTYPE html>
<html>
<head>
    <title>StreamCut Pro - Automated Video Editor</title>
</head>
<body>
    <h1>StreamCut Pro</h1>
    <p>Turn 8-hour streams into 45 minutes of content</p>

    <a href="https://github.com/IGTA-Tech/streamcut-pro/releases">Download</a>

    <h2>Pricing</h2>
    <ul>
        <li>Beta: Free</li>
        <li>Launch: $79 (limited time)</li>
        <li>Regular: $129</li>
    </ul>
</body>
</html>
```

Deploy to Netlify:
```bash
# Push to GitHub, enable Netlify deployment
# Or: netlify deploy --prod
```

---

## Update Strategy

### Releasing Updates

```bash
# 1. Make changes
# 2. Update version in src/__init__.py
# 3. Commit and tag
git commit -am "v0.2 - Added feature X"
git tag v0.2
git push && git push --tags

# 4. Build new executables
# 5. Create release
gh release create v0.2 \
  --title "StreamCut Pro v0.2" \
  --notes "**New Features:**\n- Feature X\n- Feature Y\n\n**Bug Fixes:**\n- Fixed issue Z" \
  dist/*
```

### Auto-Update (Advanced)
Consider implementing auto-update check:
- Check GitHub releases API on startup
- Notify user of updates
- Download and apply updates

---

## Success Metrics

Track these for beta:
- Number of downloads
- Active users (if adding telemetry)
- Bug reports
- Feature requests
- Processing success rate
- User testimonials

For launch:
- Sales numbers
- Conversion rate
- Customer support volume
- Refund rate

---

**You're ready to distribute! Start with GitHub releases for beta, then move to paid distribution when ready.** 🚀
