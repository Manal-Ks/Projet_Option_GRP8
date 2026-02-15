from __future__ import annotations
from typing import Dict, List

DEFAULT_WEIGHTS: Dict[str, float] = {
    "score_skills": 0.3,
    "score_experience": 0.2,
    "score_education": 0.2,
    "score_languages": 0.2,
    "score_sector": 0.1,
}

SEEDS: List[int] = [42, 123, 456]
K = 10
