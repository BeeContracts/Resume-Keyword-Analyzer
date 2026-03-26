# Resume Keyword Analyzer

A simple Python tool that compares a resume against a job description and reports:

- overall match score
- top job keywords
- matched keywords
- missing keywords
- practical suggestions for improvement

It now includes both:
- a **command-line version**
- a **simple desktop GUI** for easier use

## Why this project exists

Job seekers often tailor resumes manually and miss important keywords from job descriptions. This tool helps surface the most relevant terms quickly so a user can better align their resume with a target role.

## Features

- extracts important keywords from both inputs
- highlights overlap and gaps
- generates a weighted match score
- provides actionable suggestions
- saves text results and exports JSON
- copies results to clipboard
- supports basic text-based PDF resume loading
- supports drag-and-drop when `tkinterdnd2` is installed
- runs locally with no external API required
- includes a small GUI for easier use

## Tech Stack

- Python 3
- Tkinter for the GUI
- Standard library only

## Project Structure

```bash
resume-keyword-analyzer/
├── analyzer.py
├── gui.py
├── run_gui.bat
├── launch_gui.sh
├── sample_resume.txt
├── sample_job_description.txt
├── requirements.txt
├── .gitignore
└── README.md
```

## How to Run

### Command line

```bash
python3 analyzer.py sample_resume.txt sample_job_description.txt
```

### GUI

**Windows:**
- double-click `run_gui.bat`

**Linux / macOS:**
```bash
python3 gui.py
```

Or:
```bash
bash launch_gui.sh
```

## How the GUI Works

1. Paste your resume text into the left box
2. Paste the job description into the right box
3. Click **Analyze**
4. Review the keyword match score, missing keywords, and suggestions
5. Click **Save Text**, **Export JSON**, or **Copy Results**

You can also:
- load `.txt` files using the file buttons
- load a resume PDF using **Load Resume PDF**
- drag and drop `.txt` or `.pdf` files into the input areas if `tkinterdnd2` is installed

## PDF Support

The app includes lightweight PDF text extraction for basic text-based PDF resumes.
If a PDF does not extract cleanly, copy the resume text into a `.txt` file instead.

## Build a Real Windows .exe

See:

- `build_exe_instructions.md`
- `app_icon.ico`

The instructions include the PyInstaller command needed to package the GUI into a standalone Windows executable with a cleaner icon.

## Example Output

```text
=== Resume Keyword Analyzer ===
Overall Match Score:      61.4%
Keyword Coverage Score:   68.0%
Similarity Score:         41.7%
```

## Sample Use Cases

- tailoring a resume for technical sales roles
- checking analyst resume alignment
- identifying missing ATS keywords
- comparing multiple resumes against the same job description

## Future Improvements

- export results to JSON or CSV
- add PDF and DOCX parsing
- improve keyword ranking logic
- highlight phrases inside the original text
- package as a standalone executable

## License

MIT
