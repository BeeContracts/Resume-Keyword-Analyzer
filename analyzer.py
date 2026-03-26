#!/usr/bin/env python3
"""Resume Keyword Analyzer

Compares a resume against a job description, extracts important keywords,
and reports overlap, missing terms, and practical suggestions.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from typing import Iterable

STOPWORDS = {
    'a','an','and','are','as','at','be','by','for','from','has','have','in','is','it','its','of','on','or','that','the','to','was','were','will','with','you','your','we','our','they','their','this','these','those','not','but','if','into','than','then','them','he','she','his','her','who','what','when','where','why','how','about','over','under','using','used','use','can','ideal','candidate','role','position','seeking','required','preferred','ability'
}

PRIORITY_TERMS = {
    'python','sql','excel','tableau','power bi','api','automation','sales','sales engineering','sales engineer','engineer','engineering',
    'analyst','analysis','data','dashboard','reporting','crm','customer','workflow','operations','postgres','postgresql',
    'supabase','n8n','ai','ml','machine learning','cloud','aws','azure','google cloud','gcp','telegram','javascript',
    'customer success','customer solutions','business systems','process improvement','technical sales','integrations','dashboards'
}

PHRASE_PATTERNS = [
    r'power\s*bi',
    r'data\s+analysis',
    r'project\s+management',
    r'customer\s+success',
    r'sales\s+engineering?',
    r'sales\s+engineer',
    r'business\s+systems?',
    r'process\s+improvement',
    r'workflow\s+automation',
    r'machine\s+learning',
    r'generative\s+ai',
    r'google\s+cloud',
    r'technical\s+sales',
    r'customer\s+solutions?',
    r'cross\s+functional\s+communication',
    r'api\s+integrations?',
    r'data\s+workflows?',
    r'vector\s+database\s+integrations?',
]


def normalize_text(text: str) -> str:
    text = text.lower()
    text = text.replace('/', ' ').replace('-', ' ')
    text = re.sub(r'[^a-z0-9+.#\s]', ' ', text)
    return re.sub(r'\s+', ' ', text).strip()


def clean_term(term: str) -> str:
    term = normalize_text(term)
    replacements = {
        'apis': 'api',
        'dashboards': 'dashboard',
        'customers': 'customer',
        'integrations': 'integration',
        'communications': 'communication',
    }
    return replacements.get(term, term)


def extract_phrases(text: str) -> list[str]:
    normalized = normalize_text(text)
    found = []
    for pattern in PHRASE_PATTERNS:
        found.extend(re.findall(pattern, normalized))
    return sorted(set(clean_term(x) for x in found))


def tokenize(text: str) -> list[str]:
    normalized = normalize_text(text)
    tokens = re.findall(r'[a-z0-9+.#]{2,}', normalized)
    cleaned = [clean_term(t) for t in tokens if t not in STOPWORDS and not t.isdigit()]
    return [t for t in cleaned if t and t not in STOPWORDS]


def extract_bigrams(tokens: list[str]) -> list[str]:
    bigrams = []
    for i in range(len(tokens) - 1):
        a, b = tokens[i], tokens[i + 1]
        if a in STOPWORDS or b in STOPWORDS:
            continue
        phrase = f'{a} {b}'
        if phrase in PRIORITY_TERMS:
            bigrams.append(phrase)
    return bigrams


def score_keywords(tokens: Iterable[str], phrases: Iterable[str]) -> Counter:
    counts = Counter(tokens)
    weighted = Counter()
    for token, count in counts.items():
        weight = count
        if token in PRIORITY_TERMS:
            weight += 3
        if len(token) >= 8:
            weight += 1
        if token.endswith('ion') or token.endswith('ing'):
            weight += 0.5
        weighted[token] = weight

    for phrase in phrases:
        weighted[phrase] += 5

    return weighted


def top_keywords(text: str, limit: int = 25) -> list[str]:
    tokens = tokenize(text)
    phrases = extract_phrases(text) + extract_bigrams(tokens)
    weighted = score_keywords(tokens, phrases)
    ranked = sorted(weighted.items(), key=lambda x: (-x[1], x[0]))
    return [term for term, _ in ranked[:limit]]


def jaccard_score(a: set[str], b: set[str]) -> float:
    if not a and not b:
        return 100.0
    union = a | b
    inter = a & b
    return round((len(inter) / len(union)) * 100, 1) if union else 0.0


def coverage_score(job_keywords: list[str], resume_keywords: list[str]) -> float:
    if not job_keywords:
        return 0.0
    hits = sum(1 for kw in job_keywords if kw in set(resume_keywords))
    return round((hits / len(job_keywords)) * 100, 1)


def build_suggestions(missing: list[str]) -> list[str]:
    suggestions = []
    for kw in missing[:8]:
        suggestions.append(f'Consider adding evidence of: {kw}')
    return suggestions


def analyze(resume_text: str, job_text: str) -> dict:
    resume_keywords = top_keywords(resume_text)
    job_keywords = top_keywords(job_text)
    resume_set = set(resume_keywords)
    job_set = set(job_keywords)
    matched = sorted(job_set & resume_set)
    missing = sorted(job_set - resume_set)
    extra = sorted(resume_set - job_set)

    keyword_match = coverage_score(job_keywords, resume_keywords)
    similarity = jaccard_score(resume_set, job_set)
    overall = round((keyword_match * 0.75) + (similarity * 0.25), 1)

    return {
        'overall_score': overall,
        'keyword_match_score': keyword_match,
        'similarity_score': similarity,
        'job_keywords': job_keywords,
        'resume_keywords': resume_keywords,
        'matched_keywords': matched,
        'missing_keywords': missing,
        'extra_resume_keywords': extra[:15],
        'suggestions': build_suggestions(missing),
    }


def format_report(results: dict) -> str:
    lines = []
    lines.append('=== Resume Keyword Analyzer ===')
    lines.append(f"Overall Match Score:      {results['overall_score']}%")
    lines.append(f"Keyword Coverage Score:   {results['keyword_match_score']}%")
    lines.append(f"Similarity Score:         {results['similarity_score']}%")
    lines.append('')
    lines.append('Top Job Keywords:')
    lines.append(', '.join(results['job_keywords']))
    lines.append('')
    lines.append('Matched Keywords:')
    lines.append(', '.join(results['matched_keywords']) or 'None found')
    lines.append('')
    lines.append('Missing Keywords:')
    lines.append(', '.join(results['missing_keywords']) or 'None')
    lines.append('')
    lines.append('Extra Resume Keywords:')
    lines.append(', '.join(results['extra_resume_keywords']) or 'None')
    lines.append('')
    lines.append('Suggestions:')
    for suggestion in results['suggestions']:
        lines.append(f'- {suggestion}')
    return '\n'.join(lines)


def print_report(results: dict) -> None:
    print('\n' + format_report(results))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Compare a resume to a job description.')
    parser.add_argument('resume', type=Path, help='Path to resume text file')
    parser.add_argument('job', type=Path, help='Path to job description text file')
    parser.add_argument('--json', dest='as_json', action='store_true', help='Print JSON output')
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    resume_text = args.resume.read_text(encoding='utf-8')
    job_text = args.job.read_text(encoding='utf-8')
    results = analyze(resume_text, job_text)
    if args.as_json:
        print(json.dumps(results, indent=2))
    else:
        print_report(results)


if __name__ == '__main__':
    main()
