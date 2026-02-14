from __future__ import annotations
import pandas as pd

from schema import validate_and_coerce, CANDIDATE_SCHEMA, JOB_SCHEMA
from preprocessing import preprocess_candidates, preprocess_jobs
from pairing import build_pairs_cartesian, build_pairs_filtered_same_sector
from data_quality import quality_report_candidates, quality_report_jobs

def prepare_data_layer(df_candidates: pd.DataFrame, df_jobs: pd.DataFrame, pairing_mode: str = "cartesian"):
    # 1) validate
    df_candidates = validate_and_coerce(df_candidates, CANDIDATE_SCHEMA, "candidates")
    df_jobs = validate_and_coerce(df_jobs, JOB_SCHEMA, "jobs")

    # 2) preprocess
    df_candidates = preprocess_candidates(df_candidates)
    df_jobs = preprocess_jobs(df_jobs)

    # 3) quality report
    qc = quality_report_candidates(df_candidates)
    qj = quality_report_jobs(df_jobs)

    # 4) pairing
    if pairing_mode == "same_sector":
        pairs = build_pairs_filtered_same_sector(df_candidates, df_jobs)
    else:
        pairs = build_pairs_cartesian(df_candidates, df_jobs)

    return pairs, qc, qj
