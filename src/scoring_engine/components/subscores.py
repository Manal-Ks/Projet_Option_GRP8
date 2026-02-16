from __future__ import annotations
from typing import List, Iterable
import math
import ast
import pandas as pd


# ============================================================
# ------------------ UTILITAIRES INTERNES --------------------
# ============================================================

def _safe_list(x) -> List[str]:
    if x is None:
        return []
    if isinstance(x, list):
        return [str(i) for i in x if i]
    return [str(x)]


def _parse_list_cell(x) -> List[str]:
    """
    Convertit:
      - "['a','b']" -> ['a','b']
      - ['a','b']   -> ['a','b']
      - None/NaN    -> []
      - "a"         -> ['a']
    """
    if x is None:
        return []
    if isinstance(x, float) and math.isnan(x):
        return []
    if isinstance(x, list):
        return [str(i).strip() for i in x if i]

    s = str(x).strip()
    if not s:
        return []

    # Si c'est une liste stockée en string
    if s.startswith("[") and s.endswith("]"):
        try:
            parsed = ast.literal_eval(s)
            if isinstance(parsed, list):
                return [str(i).strip() for i in parsed if i]
        except Exception:
            pass

    return [s]


def _edu_to_num(x) -> int:
    """
    Convertit "bac+5" -> 5 ; "Bac+3" -> 3 ; None -> 0
    """
    if x is None:
        return 0
    if isinstance(x, float) and math.isnan(x):
        return 0

    s = str(x).lower().replace(" ", "")
    if "bac+" in s:
        try:
            return int(s.split("bac+")[1])
        except Exception:
            return 0

    try:
        return int(float(s))
    except Exception:
        return 0


# ============================================================
# -------------------- SCORES UNITAIRES ----------------------
# ============================================================

def skills_jaccard(cand_skills: Iterable[str], job_skills: Iterable[str]) -> float:
    a = set(_safe_list(cand_skills))
    b = set(_safe_list(job_skills))
    if not a or not b:
        return 0.0
    return float(len(a & b) / len(a | b))


def experience_score(candidate_years, job_min_years) -> float:
    try:
        cand = float(candidate_years) if candidate_years is not None else 0.0
    except Exception:
        cand = 0.0

    try:
        job = float(job_min_years) if job_min_years is not None else 0.0
    except Exception:
        job = 0.0

    if job <= 0.0:
        return float(max(0.0, min(1.0, cand / 2.0)))

    if cand >= job:
        return float(max(0.0, min(1.0, cand / (job + 2.0))))

    ratio = cand / job if job > 0 else 0.0
    return float(max(0.0, min(1.0, ratio ** 1.5)))


def education_score(candidate_level, job_level) -> float:
    try:
        cand = int(candidate_level) if candidate_level is not None else 0
    except Exception:
        cand = 0

    try:
        job = int(job_level) if job_level is not None else 1
    except Exception:
        job = 1

    if cand <= 0:
        return 0.0

    if job <= 0:
        job = 1

    if cand >= job:
        return 1.0

    return float(max(0.0, min(1.0, (cand / job) ** 2)))


def languages_score(candidate_langs, job_langs) -> float:
    a = set(_safe_list(candidate_langs))
    b = set(_safe_list(job_langs))

    if not b:
        return 1.0

    if not a:
        return 0.0

    return float(len(a & b) / len(b))


def sector_score(candidate_sector, job_sector) -> float:
    if not candidate_sector or not job_sector:
        return 0.0
    return 1.0 if str(candidate_sector) == str(job_sector) else 0.5


# ============================================================
# ----------------- FONCTION GLOBALE PARTIE 4 ----------------
# ============================================================

def compute_subscores(pairs_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcule les 5 subscores sur le DataFrame des paires candidat-offre.

    Colonnes attendues (compatibles avec tes CSV) :
      - candidate_skills / required_skills
      - years_experience / min_experience
      - education_level / required_education
      - languages / required_languages
      - sector / required_sector
    """

    df = pairs_df.copy()

    # Mapping colonnes
    cand_skills_col = "candidate_skills" if "candidate_skills" in df.columns else "skills"
    job_skills_col = "required_skills"

    cand_exp_col = "years_experience"
    job_exp_col = "min_experience"

    cand_edu_col = "education_level"
    job_edu_col = "required_education"

    cand_lang_col = "languages"
    job_lang_col = "required_languages"

    cand_sector_col = "sector"
    job_sector_col = "required_sector"

    # Sécurité si colonnes absentes
    for col in [
        cand_skills_col, job_skills_col,
        cand_exp_col, job_exp_col,
        cand_edu_col, job_edu_col,
        cand_lang_col, job_lang_col,
        cand_sector_col, job_sector_col
    ]:
        if col not in df.columns:
            df[col] = None

    # Parsing listes
    df["_cand_skills_list"] = df[cand_skills_col].apply(_parse_list_cell)
    df["_job_skills_list"] = df[job_skills_col].apply(_parse_list_cell)

    df["_cand_lang_list"] = df[cand_lang_col].apply(_parse_list_cell)
    df["_job_lang_list"] = df[job_lang_col].apply(_parse_list_cell)

    # Education → numérique
    df["_cand_edu_num"] = df[cand_edu_col].apply(_edu_to_num)
    df["_job_edu_num"] = df[job_edu_col].apply(_edu_to_num)

    # Calcul scores
    df["score_skills"] = df.apply(
        lambda r: skills_jaccard(r["_cand_skills_list"], r["_job_skills_list"]), axis=1
    )

    df["score_experience"] = df.apply(
        lambda r: experience_score(r[cand_exp_col], r[job_exp_col]), axis=1
    )

    df["score_education"] = df.apply(
        lambda r: education_score(r["_cand_edu_num"], r["_job_edu_num"]), axis=1
    )

    df["score_languages"] = df.apply(
        lambda r: languages_score(r["_cand_lang_list"], r["_job_lang_list"]), axis=1
    )

    df["score_sector"] = df.apply(
        lambda r: sector_score(r[cand_sector_col], r[job_sector_col]), axis=1
    )

    # Clamp sécurité [0,1]
    for c in [
        "score_skills",
        "score_experience",
        "score_education",
        "score_languages",
        "score_sector"
    ]:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0.0).clip(0.0, 1.0)

    # Nettoyage colonnes temporaires
    df.drop(columns=[c for c in df.columns if c.startswith("_")],
            inplace=True,
            errors="ignore")

    return df
