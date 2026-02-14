# src/ats_scoring/preprocessing.py
from __future__ import annotations
import re
import unicodedata
from typing import Any, List
import pandas as pd

_SPLIT_PATTERN = re.compile(r"[;,|/]+")

def strip_accents(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    return "".join(ch for ch in s if not unicodedata.combining(ch))

def normalize_text(x: Any) -> str:
    if x is None or (isinstance(x, float) and pd.isna(x)):
        return ""
    s = str(x).strip().lower()
    s = strip_accents(s)
    s = re.sub(r"\s+", " ", s)
    return s

def to_list(x: Any) -> List[str]:
    if x is None or (isinstance(x, float) and pd.isna(x)):
        return []
    if isinstance(x, list):
        items = x
    else:
        s = str(x).strip()
        if not s:
            return []
        s = s.strip("[](){}")
        items = _SPLIT_PATTERN.split(s)

    normed = []
    for it in items:
        t = normalize_text(it)
        if t:
            normed.append(t)

    seen = set()
    out = []
    for t in normed:
        if t not in seen:
            seen.add(t)
            out.append(t)
    return out

def preprocess_candidates(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["candidate_id"] = out["candidate_id"].astype(str)

    out["candidate_skills"] = out["candidate_skills"].apply(to_list)
    out["languages"] = out["languages"].apply(to_list)

    out["education_level"] = out["education_level"].apply(normalize_text)
    out["sector"] = out["sector"].apply(normalize_text)

    out["years_experience"] = pd.to_numeric(out["years_experience"], errors="coerce").fillna(0.0)
    return out

def preprocess_jobs(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["job_id"] = out["job_id"].astype(str)

    out["required_skills"] = out["required_skills"].apply(to_list)
    out["required_languages"] = out["required_languages"].apply(to_list)

    out["required_education"] = out["required_education"].apply(normalize_text)
    out["required_sector"] = out["required_sector"].apply(normalize_text)

    out["min_experience"] = pd.to_numeric(out["min_experience"], errors="coerce").fillna(0.0)
    return out

