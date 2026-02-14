from __future__ import annotations
import pandas as pd

def build_pairs_cartesian(df_candidates: pd.DataFrame, df_jobs: pd.DataFrame) -> pd.DataFrame:
    c = df_candidates.copy()
    j = df_jobs.copy()
    c["_key"] = 1
    j["_key"] = 1
    pairs = c.merge(j, on="_key", how="inner").drop(columns=["_key"])
    return pairs


def build_pairs_filtered_same_sector(df_candidates: pd.DataFrame, df_jobs: pd.DataFrame) -> pd.DataFrame:
    return df_candidates.merge(df_jobs, left_on="sector", right_on="required_sector", how="inner")

