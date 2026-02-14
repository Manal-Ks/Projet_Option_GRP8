# src/ats_scoring/schema.py
from __future__ import annotations
from dataclasses import dataclass
from typing import List
import pandas as pd

@dataclass(frozen=True)
class SchemaSpec:
    required_cols: List[str]
    list_cols: List[str]
    numeric_cols: List[str]
    text_cols: List[str]
    id_cols: List[str]

CANDIDATE_SCHEMA = SchemaSpec(
    required_cols=[
        "candidate_id",
        "candidate_skills",
        "years_experience",
        "education_level",
        "languages",
        "sector",
    ],
    list_cols=["candidate_skills", "languages"],
    numeric_cols=["years_experience"],
    text_cols=["education_level", "sector"],
    id_cols=["candidate_id"],
)

JOB_SCHEMA = SchemaSpec(
    required_cols=[
        "job_id",
        "required_skills",
        "min_experience",
        "required_education",
        "required_languages",
        "required_sector",
    ],
    list_cols=["required_skills", "required_languages"],
    numeric_cols=["min_experience"],
    text_cols=["required_education", "required_sector"],
    id_cols=["job_id"],
)

class SchemaError(ValueError):
    pass

def validate_required_columns(df: pd.DataFrame, spec: SchemaSpec, df_name: str) -> None:
    missing = [c for c in spec.required_cols if c not in df.columns]
    if missing:
        raise SchemaError(f"{df_name}: missing required columns: {missing}")

def coerce_numeric(df: pd.DataFrame, cols: List[str]) -> pd.DataFrame:
    out = df.copy()
    for c in cols:
        out[c] = pd.to_numeric(out[c], errors="coerce")
    return out

def ensure_unique_ids(df: pd.DataFrame, id_col: str, df_name: str) -> None:
    if df[id_col].isna().any():
        raise SchemaError(f"{df_name}: id column '{id_col}' contains nulls")
    if df[id_col].duplicated().any():
        raise SchemaError(f"{df_name}: id column '{id_col}' contains duplicates")

def validate_and_coerce(df: pd.DataFrame, spec: SchemaSpec, df_name: str) -> pd.DataFrame:
    validate_required_columns(df, spec, df_name)
    out = coerce_numeric(df, spec.numeric_cols)
    for idc in spec.id_cols:
        ensure_unique_ids(out, idc, df_name)
    return out

