#!/usr/bin/env python3
"""Simple GUI for Resume Keyword Analyzer."""

from __future__ import annotations

import json
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, scrolledtext

from analyzer import analyze, format_report
from pdf_utils import extract_text_from_pdf

try:
    from tkinterdnd2 import DND_FILES, TkinterDnD  # type: ignore
    HAS_DND = True
except Exception:
    DND_FILES = None
    TkinterDnD = None
    HAS_DND = False

APP_BG = '#0f172a'
PANEL_BG = '#111827'
ACCENT = '#38bdf8'
TEXT = '#e5e7eb'
MUTED = '#94a3b8'
BUTTON = '#1f2937'


class AnalyzerApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title('Resume Keyword Analyzer')
        self.root.geometry('1040x800')
        self.root.configure(bg=APP_BG)
        self.last_output = ''
        self.last_results = None
        self._set_icon_if_available()

        title = tk.Label(root, text='Resume Keyword Analyzer', font=('Segoe UI', 18, 'bold'), bg=APP_BG, fg=TEXT)
        title.pack(pady=(12, 4))

        subtitle_text = 'Paste resume text and a job description, then analyze keyword overlap.'
        if HAS_DND:
            subtitle_text += ' Drag-and-drop .txt or .pdf files into the Resume box.'
        subtitle = tk.Label(root, text=subtitle_text, font=('Segoe UI', 10), bg=APP_BG, fg=MUTED)
        subtitle.pack(pady=(0, 10))

        top_frame = tk.Frame(root, bg=APP_BG)
        top_frame.pack(fill='both', expand=True, padx=12)

        left = tk.Frame(top_frame, bg=APP_BG)
        left.pack(side='left', fill='both', expand=True, padx=(0, 6))
        right = tk.Frame(top_frame, bg=APP_BG)
        right.pack(side='left', fill='both', expand=True, padx=(6, 0))

        tk.Label(left, text='Resume Text', font=('Segoe UI', 11, 'bold'), bg=APP_BG, fg=TEXT).pack(anchor='w')
        self.resume_text = scrolledtext.ScrolledText(left, wrap='word', height=18, bg=PANEL_BG, fg=TEXT, insertbackground=TEXT)
        self.resume_text.pack(fill='both', expand=True)
        self._enable_drop(self.resume_text, is_resume=True)

        resume_buttons = tk.Frame(left, bg=APP_BG)
        resume_buttons.pack(anchor='w', pady=6)
        self._button(resume_buttons, 'Load Resume Text File', self.load_resume_text).pack(side='left')
        self._button(resume_buttons, 'Load Resume PDF', self.load_resume_pdf).pack(side='left', padx=6)

        tk.Label(right, text='Job Description Text', font=('Segoe UI', 11, 'bold'), bg=APP_BG, fg=TEXT).pack(anchor='w')
        self.job_text = scrolledtext.ScrolledText(right, wrap='word', height=18, bg=PANEL_BG, fg=TEXT, insertbackground=TEXT)
        self.job_text.pack(fill='both', expand=True)
        self._enable_drop(self.job_text, is_resume=False)

        self._button(right, 'Load Job Description Text File', self.load_job).pack(anchor='w', pady=6)

        button_row = tk.Frame(root, bg=APP_BG)
        button_row.pack(fill='x', padx=12, pady=10)
        self._button(button_row, 'Analyze', self.run_analysis, bold=True).pack(side='left')
        self._button(button_row, 'Save Text', self.save_results_text).pack(side='left', padx=8)
        self._button(button_row, 'Export JSON', self.save_results_json).pack(side='left')
        self._button(button_row, 'Copy Results', self.copy_results).pack(side='left', padx=8)
        self._button(button_row, 'Clear', self.clear_all).pack(side='left')

        tk.Label(root, text='Results', font=('Segoe UI', 11, 'bold'), bg=APP_BG, fg=TEXT).pack(anchor='w', padx=12)
        self.results = scrolledtext.ScrolledText(root, wrap='word', height=17, bg=PANEL_BG, fg=TEXT, insertbackground=TEXT)
        self.results.pack(fill='both', expand=True, padx=12, pady=(0, 12))

    def _button(self, parent, text, command, bold=False):
        return tk.Button(parent, text=text, command=command, bg=BUTTON, fg=TEXT, activebackground=ACCENT, activeforeground='black', relief='flat', padx=10, pady=6, font=('Segoe UI', 10, 'bold' if bold else 'normal'))

    def _set_icon_if_available(self) -> None:
        icon = Path(__file__).with_name('app_icon.png')
        if icon.exists():
            try:
                photo = tk.PhotoImage(file=str(icon))
                self.root.iconphoto(True, photo)
                self._icon_ref = photo
            except Exception:
                pass

    def _enable_drop(self, widget, is_resume: bool) -> None:
        if not HAS_DND:
            return
        widget.drop_target_register(DND_FILES)
        widget.dnd_bind('<<Drop>>', lambda event: self._handle_drop(event, is_resume))

    def _handle_drop(self, event, is_resume: bool) -> None:
        raw = event.data.strip()
        path = raw[1:-1] if raw.startswith('{') and raw.endswith('}') else raw
        p = Path(path)
        if not p.exists():
            return
        target = self.resume_text if is_resume else self.job_text
        if p.suffix.lower() == '.pdf' and is_resume:
            try:
                text = extract_text_from_pdf(p)
                target.delete('1.0', tk.END)
                target.insert(tk.END, text)
            except Exception as e:
                messagebox.showerror('PDF Error', f'Failed to read PDF: {e}')
        else:
            try:
                text = p.read_text(encoding='utf-8')
                target.delete('1.0', tk.END)
                target.insert(tk.END, text)
            except Exception as e:
                messagebox.showerror('File Error', f'Failed to read file: {e}')

    def load_text_into(self, widget: scrolledtext.ScrolledText) -> None:
        path = filedialog.askopenfilename(filetypes=[('Text files', '*.txt'), ('All files', '*.*')])
        if not path:
            return
        with open(path, 'r', encoding='utf-8') as f:
            widget.delete('1.0', tk.END)
            widget.insert(tk.END, f.read())

    def load_resume_text(self) -> None:
        self.load_text_into(self.resume_text)

    def load_resume_pdf(self) -> None:
        path = filedialog.askopenfilename(filetypes=[('PDF files', '*.pdf')])
        if not path:
            return
        try:
            text = extract_text_from_pdf(path)
            if not text:
                messagebox.showwarning('PDF Read Issue', 'Could not extract readable text from that PDF. Try copying the resume into a .txt file instead.')
                return
            self.resume_text.delete('1.0', tk.END)
            self.resume_text.insert(tk.END, text)
        except Exception as e:
            messagebox.showerror('PDF Error', f'Failed to read PDF: {e}')

    def load_job(self) -> None:
        self.load_text_into(self.job_text)

    def clear_all(self) -> None:
        self.resume_text.delete('1.0', tk.END)
        self.job_text.delete('1.0', tk.END)
        self.results.delete('1.0', tk.END)
        self.last_output = ''
        self.last_results = None

    def run_analysis(self) -> None:
        resume = self.resume_text.get('1.0', tk.END).strip()
        job = self.job_text.get('1.0', tk.END).strip()
        if not resume or not job:
            messagebox.showwarning('Missing Input', 'Please provide both resume text and a job description.')
            return

        data = analyze(resume, job)
        self.last_results = data
        self.last_output = format_report(data)
        self.results.delete('1.0', tk.END)
        self.results.insert(tk.END, self.last_output)

    def save_results_text(self) -> None:
        if not self.last_output.strip():
            messagebox.showinfo('Nothing to Save', 'Run an analysis first, then save the results.')
            return
        path = filedialog.asksaveasfilename(defaultextension='.txt', filetypes=[('Text files', '*.txt'), ('All files', '*.*')], initialfile='resume_keyword_analysis.txt')
        if not path:
            return
        Path(path).write_text(self.last_output, encoding='utf-8')
        messagebox.showinfo('Saved', f'Results saved to:\n{path}')

    def save_results_json(self) -> None:
        if not self.last_results:
            messagebox.showinfo('Nothing to Export', 'Run an analysis first, then export the JSON.')
            return
        path = filedialog.asksaveasfilename(defaultextension='.json', filetypes=[('JSON files', '*.json'), ('All files', '*.*')], initialfile='resume_keyword_analysis.json')
        if not path:
            return
        Path(path).write_text(json.dumps(self.last_results, indent=2), encoding='utf-8')
        messagebox.showinfo('Saved', f'JSON exported to:\n{path}')

    def copy_results(self) -> None:
        if not self.last_output.strip():
            messagebox.showinfo('Nothing to Copy', 'Run an analysis first, then copy the results.')
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(self.last_output)
        self.root.update()
        messagebox.showinfo('Copied', 'Results copied to clipboard.')


def create_root():
    if HAS_DND and TkinterDnD is not None:
        return TkinterDnD.Tk()
    return tk.Tk()


if __name__ == '__main__':
    root = create_root()
    app = AnalyzerApp(root)
    root.mainloop()
