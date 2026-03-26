# Build a Windows .exe for Resume Keyword Analyzer

These instructions let you package the GUI app into a standalone Windows executable.

## Best way
Do this on a **Windows machine** with Python installed.

## 1) Open terminal in the project folder
Example:

```bash
cd path\to\resume-keyword-analyzer
```

## 2) Create and activate a virtual environment (optional but recommended)

```bash
python -m venv .venv
.venv\Scripts\activate
```

## 3) Install PyInstaller

```bash
pip install pyinstaller
```

## 4) Install optional drag-and-drop support (recommended)

```bash
pip install tkinterdnd2
```

## 5) Build the .exe

```bash
pyinstaller --onefile --windowed --name ResumeKeywordAnalyzer --icon app_icon.ico gui.py
```

## 6) Find the finished .exe
It will be created here:

```bash
dist\ResumeKeywordAnalyzer.exe
```

## Notes
- `--windowed` prevents a console window from opening behind the app.
- `--onefile` packages everything into a single executable.
- `--icon app_icon.ico` gives the app a cleaner branded icon.
- If Windows Defender complains, you may need to click **More info -> Run anyway** for unsigned apps.
- Drag-and-drop support uses `tkinterdnd2`; if you skip that install, the GUI still works, just without drag-and-drop.

## Optional icon
If you have an `.ico` file, you can build with:

```bash
pyinstaller --onefile --windowed --name ResumeKeywordAnalyzer --icon app.ico gui.py
```

## If something fails
Try rebuilding clean:

```bash
pyinstaller --clean --onefile --windowed --name ResumeKeywordAnalyzer gui.py
```

## What to upload to GitHub
You should upload the source code, not the generated `dist/` folder by default.
If you want to share the `.exe`, use GitHub Releases or Google Drive.
