from __future__ import annotations
from typing import List, Iterable
import math

def _safe_list(x) -> List[str]:
    if x is None:
        return []
    if isinstance(x, list):
        return [str(i) for i in x if i]
    return [str(x)]


def skills_jaccard(cand_skills: Iterable[str], job_skills: Iterable[str]) -> float:
    a = set(_safe_list(cand_skills))
    b = set(_safe_list(job_skills))
    if not a or not b:
        return 0.0
    return float(len(a & b) / len(a | b))


def experience_score(candidate_years, job_min_years) -> float:
    try:
        cand = float(candidate_years) if candidate_years is not None else 0.0
    except Exception:
        cand = 0.0
    try:
        job = float(job_min_years) if job_min_years is not None else 0.0
    except Exception:
        job = 0.0

    if job <= 0.0:
        return float(max(0.0, min(1.0, cand / 2.0)))
    if cand >= job:
        return float(max(0.0, min(1.0, cand / (job + 2.0))))
    ratio = cand / job if job > 0 else 0.0
    return float(max(0.0, min(1.0, ratio ** 1.5)))


def education_score(candidate_level, job_level) -> float:
    try:
        cand = int(candidate_level) if candidate_level is not None else 0
    except Exception:
        cand = 0
    try:
        job = int(job_level) if job_level is not None else 1
    except Exception:
        job = 1
    if cand <= 0:
        return 0.0
    if job <= 0:
        job = 1
    if cand >= job:
        return 1.0
    return float(max(0.0, min(1.0, (cand / job) ** 2)))


def languages_score(candidate_langs, job_langs) -> float:
    a = set(_safe_list(candidate_langs))
    b = set(_safe_list(job_langs))
    if not b:
        return 1.0
    if not a:
        return 0.0
    return float(len(a & b) / len(b))


def sector_score(candidate_sector, job_sector) -> float:
    if not candidate_sector or not job_sector:
        return 0.0
    return 1.0 if str(candidate_sector) == str(job_sector) else 0.5
