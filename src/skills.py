from __future__ import annotations
from typing import List, Dict, Optional, Union
import re
import pandas as pd

# Small master mapping: keys are lower-cased source phrases, values are canonical skill ids
SKILL_MASTER_DICT: Dict[str, str] = {
    "ms excel": "excel",
    "excel": "excel",
    "microsoft excel": "excel",
    "machine learning": "machine_learning",
    "ml": "machine_learning",
    "data analysis": "data_analysis",
    "python": "python",
    "r": "r",
}

# Reverse mapping is rarely necessary here but provided for completeness
REVERSE_SKILL_MAP: Dict[str, str] = {v: v for v in set(SKILL_MASTER_DICT.values())}


def _snake_case(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r"[^a-z0-9]+", "_", s)
    s = re.sub(r"_+", "_", s)
    return s.strip("_")


def normalize_single_skill(skill: Union[str, None]) -> str:
    if skill is None or (isinstance(skill, float) and pd.isna(skill)):
        return ""
    s = str(skill).strip().lower()
    if not s:
        return ""

    # exact mapping first
    if s in SKILL_MASTER_DICT:
        return SKILL_MASTER_DICT[s]

    # fallback to snake_case
    return _snake_case(s)


def normalize_skills(skills: Union[List[str], str, None]) -> List[str]:
    if skills is None or (isinstance(skills, float) and pd.isna(skills)):
        return []

    # accept either a list or a single string; if string looks like python list, we leave parsing to caller
    items: List[str]
    if isinstance(skills, list):
        items = skills
    else:
        # if it's a single string, split on common delimiters
        s = str(skills).strip()
        if not s:
            return []
        items = re.split(r"[;,|/]+|\\s+", s)

    normed = [normalize_single_skill(it) for it in items if it is not None]
    uniq = []
    seen = set()
    for v in normed:
        if v and v not in seen:
            seen.add(v)
            uniq.append(v)
    return uniq
