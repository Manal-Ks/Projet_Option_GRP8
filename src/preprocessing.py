from __future__ import annotations
import re
import unicodedata
from typing import Any, List
import pandas as pd
import ast
from .education import normalize_education
from .languages import normalize_languages
from .skills import normalize_skills
from .sector import normalize_sector

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
    """
    Robust list parser:
    - list[str] -> normalize items
    - "a,b;c|d" -> split
    - "['a','b']" -> parsed via ast.literal_eval
    - None/NaN -> []
    """
    if x is None or (isinstance(x, float) and pd.isna(x)):
        return []

    # already a list
    if isinstance(x, list):
        items = x

    else:
        s = str(x).strip()
        if not s:
            return []

        # try python-list-like string
        if (s.startswith("[") and s.endswith("]")) or (s.startswith("(") and s.endswith(")")):
            try:
                parsed = ast.literal_eval(s)
                if isinstance(parsed, list):
                    items = parsed
                else:
                    items = [parsed]
            except Exception:
                s = s.strip("[](){}")
                items = _SPLIT_PATTERN.split(s)
        else:
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

    # skills -> parse list then normalize canonical skill ids
    out["candidate_skills"] = out["candidate_skills"].apply(to_list).apply(normalize_skills)

    # languages -> parse list then normalize codes
    out["languages"] = out["languages"].apply(to_list).apply(normalize_languages)

    # education: keep normalized text and add numeric column
    out["education_level"] = out["education_level"].apply(normalize_text)
    out["education_level_num"] = out["education_level"].apply(normalize_education)

    # sector -> canonical representation
    out["sector"] = out["sector"].apply(normalize_sector)

    out["years_experience"] = pd.to_numeric(out["years_experience"], errors="coerce").fillna(0.0)
    return out

def preprocess_jobs(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["job_id"] = out["job_id"].astype(str)

    out["required_skills"] = out["required_skills"].apply(to_list).apply(normalize_skills)
    out["required_languages"] = out["required_languages"].apply(to_list).apply(normalize_languages)

    out["required_education"] = out["required_education"].apply(normalize_text)
    out["required_education_num"] = out["required_education"].apply(normalize_education)

    out["required_sector"] = out["required_sector"].apply(normalize_sector)

    out["min_experience"] = pd.to_numeric(out["min_experience"], errors="coerce").fillna(0.0)
    return out

