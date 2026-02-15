from __future__ import annotations
from typing import Union
import re
import pandas as pd

# canonical mapping for common sectors
_SECTOR_CANONICAL = {
    "it": "it_data",
    "it/data": "it_data",
    "it data": "it_data",
    "data": "it_data",
    "data science": "it_data",
    "consulting": "consulting",
    "audit": "audit",
    "finance": "finance",
    "health": "healthcare",
}


def _norm_text(x: Union[str, float, None]) -> str:
    if x is None or (isinstance(x, float) and pd.isna(x)):
        return ""
    s = str(x).strip().lower()
    s = re.sub(r"[^a-z0-9]+", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def _to_snake(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r"[^a-z0-9]+", "_", s)
    s = re.sub(r"_+", "_", s)
    return s.strip("_")


def normalize_sector(sector: Union[str, float, None]) -> str:
    s = _norm_text(sector)
    if not s:
        return "unknown"

    # direct canonical matches
    if s in _SECTOR_CANONICAL:
        return _SECTOR_CANONICAL[s]

    # try token-level matching
    for key, val in _SECTOR_CANONICAL.items():
        if key in s:
            return val

    # fallback to snake_case representation
    return _to_snake(s)


def is_same_sector(a: Union[str, None], b: Union[str, None]) -> bool:
    return normalize_sector(a) == normalize_sector(b)
