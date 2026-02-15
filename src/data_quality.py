from __future__ import annotations
import pandas as pd

def quality_report_candidates(df: pd.DataFrame) -> dict:
    return {
        "n_rows": len(df),
        "pct_empty_skills": (df["candidate_skills"].apply(len) == 0).mean(),
        "pct_missing_languages": (df["languages"].apply(len) == 0).mean(),
        "pct_missing_sector": (df["sector"].isin(["", "unknown"]) ).mean(),
        "pct_missing_education": (df["education_level"].eq("")).mean(),
    }

def quality_report_jobs(df: pd.DataFrame) -> dict:
    return {
        "n_rows": len(df),
        "pct_empty_required_skills": (df["required_skills"].apply(len) == 0).mean(),
        "pct_empty_required_languages": (df["required_languages"].apply(len) == 0).mean(),
        "pct_missing_required_sector": (df["required_sector"].isin(["", "unknown"]) ).mean(),
        "pct_missing_required_education": (df["required_education"].eq("")).mean(),
    }
