from __future__ import annotations
import re
from typing import Union
import pandas as pd


def _norm_text(x: Union[str, float, None]) -> str:
    if x is None or (isinstance(x, float) and pd.isna(x)):
        return ""
    return str(x).strip().lower()


def normalize_education(education: Union[str, float, None]) -> int:
    """Normalize education level to an integer.

    Recognises patterns like "bac+3", "bac + 5" and returns the numeric part
    when it is 3,4 or 5. Otherwise returns 0.
    """
    s = _norm_text(education)
    if not s:
        return 0

    # look for patterns like 'bac+5' or 'bac + 4'
    m = re.search(r"bac\s*\+\s*(\d+)", s)
    if not m:
        m = re.search(r"bac\s*(\d+)", s)
    if m:
        try:
            val = int(m.group(1))
            if val in (3, 4, 5):
                return val
        except Exception:
            return 0
    return 0


def validate_education(level: int) -> bool:
    return isinstance(level, int) and level in (3, 4, 5)
