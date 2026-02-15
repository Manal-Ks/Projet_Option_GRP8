from __future__ import annotations
import re
from typing import List, Union
import ast
import pandas as pd

_SPLIT_PATTERN = re.compile(r"[;,|/]+")


def _to_items(x: Union[str, List[str], None]) -> List[str]:
    if x is None or (isinstance(x, float) and pd.isna(x)):
        return []
    if isinstance(x, list):
        items = x
    else:
        s = str(x).strip()
        if not s:
            return []
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
    return [str(i) for i in items if i is not None]


def normalize_languages(languages: Union[str, List[str], None]) -> List[str]:
    """Return a normalized, unique, sorted list of language codes.

    Normalization rules:
    - parse lists and delimited strings
    - lowercase + strip
    - keep only alphabetic tokens of length 2-3
    - deduplicate and sort
    """
    items = _to_items(languages)
    normed = []
    for it in items:
        t = str(it).strip().lower()
        t = re.sub(r"[^a-z]", "", t)
        if 2 <= len(t) <= 3:
            normed.append(t)
    uniq = sorted(set(normed))
    return uniq


def languages_overlap_count(a: List[str], b: List[str]) -> int:
    return len(set(a) & set(b))


def languages_overlap_ratio(a: List[str], b: List[str]) -> float:
    a_set = set(a)
    if not a_set:
        return 0.0
    return len(a_set & set(b)) / len(a_set)
