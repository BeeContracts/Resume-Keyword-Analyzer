#!/usr/bin/env python3
"""Minimal PDF text extraction using standard library only.
Supports simple text-based PDFs for lightweight local use.
"""

from __future__ import annotations

import re
import zlib
from pathlib import Path


def extract_text_from_pdf(path: str | Path) -> str:
    data = Path(path).read_bytes()
    streams = re.findall(rb'stream\r?\n(.*?)\r?\nendstream', data, re.S)
    chunks: list[str] = []

    for raw in streams:
        for candidate in (raw, _try_decompress(raw)):
            if not candidate:
                continue
            text = _extract_text_operators(candidate)
            if text.strip():
                chunks.append(text)

    result = '\n'.join(chunks)
    result = re.sub(r'\s+', ' ', result).strip()
    return result


def _try_decompress(blob: bytes) -> bytes | None:
    try:
        return zlib.decompress(blob)
    except Exception:
        return None


def _extract_text_operators(blob: bytes) -> str:
    parts: list[str] = []

    for match in re.finditer(rb'\((.*?)\)\s*Tj', blob, re.S):
        parts.append(_decode_pdf_string(match.group(1)))

    for match in re.finditer(rb'\[(.*?)\]\s*TJ', blob, re.S):
        arr = match.group(1)
        inner = re.findall(rb'\((.*?)\)', arr, re.S)
        if inner:
            parts.append(''.join(_decode_pdf_string(x) for x in inner))

    return '\n'.join(parts)


def _decode_pdf_string(raw: bytes) -> str:
    raw = raw.replace(rb'\(', b'(').replace(rb'\)', b')').replace(rb'\\', b'\\')
    try:
        return raw.decode('utf-8', errors='ignore')
    except Exception:
        return raw.decode('latin-1', errors='ignore')
