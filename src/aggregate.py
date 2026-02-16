# src/aggregate.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Iterable, List
import numpy as np
import pandas as pd


SUBSCORE_COLS = ["score_skills", "score_experience", "score_education", "score_languages", "score_sector"]


@dataclass(frozen=True)
class WeightConfig:
    skills: float = 0.35
    experience: float = 0.20
    education: float = 0.15
    languages: float = 0.15
    sector: float = 0.15

    def as_dict(self) -> Dict[str, float]:
        return {
            "score_skills": self.skills,
            "score_experience": self.experience,
            "score_education": self.education,
            "score_languages": self.languages,
            "score_sector": self.sector,
        }


def make_vector_score(df: pd.DataFrame) -> pd.DataFrame:
    missing = [c for c in SUBSCORE_COLS if c not in df.columns]
    if missing:
        raise KeyError(f"Missing subscores columns: {missing}")

    out = df.copy()
    out["vector_score"] = out[SUBSCORE_COLS].apply(lambda r: r.to_list(), axis=1)
    return out


def weighted_global_score(df: pd.DataFrame, weights: WeightConfig) -> pd.DataFrame:
    w = weights.as_dict()
    wsum = float(sum(w.values()))
    if wsum <= 0:
        raise ValueError("Sum of weights must be > 0")

    out = df.copy()
    # Normalisation optionnelle: si l’utilisateur met des poids qui ne somment pas à 1
    for k in w:
        w[k] = w[k] / wsum

    # Score = somme pondérée
    out["global_score"] = (
        out["score_skills"] * w["score_skills"]
        + out["score_experience"] * w["score_experience"]
        + out["score_education"] * w["score_education"]
        + out["score_languages"] * w["score_languages"]
        + out["score_sector"] * w["score_sector"]
    )

    # clamp robuste [0,1]
    out["global_score"] = out["global_score"].clip(0.0, 1.0)
    return out


def select_output_columns(df: pd.DataFrame, keep_cols: List[str] | None = None) -> pd.DataFrame:
    keep_cols = keep_cols or []
    base = [c for c in keep_cols if c in df.columns]
    cols = base + SUBSCORE_COLS + ["global_score", "vector_score"]
    cols = [c for c in cols if c in df.columns]
    return df[cols].copy()
