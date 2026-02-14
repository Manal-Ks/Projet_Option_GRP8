# Generates:
#   data/dev/candidates_dev.csv
#   data/dev/jobs_dev.csv
#   data/samples/candidates_sample.csv
#   data/samples/jobs_sample.csv

from __future__ import annotations

import os
import random
from dataclasses import dataclass
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd


# -----------------------------
# Config
# -----------------------------
@dataclass
class GenConfig:
    n_candidates: int = 10000
    n_jobs: int = 200
    seed: int = 42

    # Where to write outputs
    dev_dir: str = "data/dev"
    samples_dir: str = "data/samples"

    # Noise controls
    p_missing_languages: float = 0.03
    p_missing_sector: float = 0.01
    p_missing_education: float = 0.01
    p_typo_in_skill: float = 0.04
    p_synonym_skill: float = 0.08
    p_mix_fr_en_skill: float = 0.06

    # Candidate skills distribution
    min_skills: int = 4
    max_skills: int = 12

    # Job required skills distribution
    min_req_skills: int = 4
    max_req_skills: int = 10

    # Sector mix
    sector_probs: Dict[str, float] = None  # set in __post_init__

    # Education distribution
    education_levels: Tuple[str, ...] = ("bac+3", "bac+4", "bac+5")
    education_probs: Tuple[float, ...] = (0.35, 0.10, 0.55)

    # Language pools
    language_pool: Tuple[str, ...] = ("fr", "en", "es", "ar")
    language_probs: Tuple[float, ...] = (0.60, 0.30, 0.07, 0.03)

    # Jobs language requirements
    min_req_lang: int = 1
    max_req_lang: int = 2

    # Experience
    max_years_experience: int = 8


def _ensure_dirs(*paths: str) -> None:
    for p in paths:
        os.makedirs(p, exist_ok=True)


def _set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)


# -----------------------------
# Skill pools & synonyms/typos
# -----------------------------
SECTOR_CANONICAL = {
    "audit": "audit",
    "consulting": "consulting",
    "it / data": "it / data",
    "it/data": "it / data",
    "it-data": "it / data",
    "it data": "it / data",
}

SKILLS_BY_SECTOR = {
    "audit": [
        "audit", "ifrs", "consolidation", "excel", "financial analysis", "accounting",
        "internal control", "risk assessment", "due diligence", "sap", "power bi"
    ],
    "consulting": [
        "strategy", "business analysis", "powerpoint", "stakeholder management", "communication",
        "project management", "problem solving", "market research", "excel", "data analysis"
    ],
    "it / data": [
        "python", "sql", "data engineering", "machine learning", "cloud", "aws",
        "azure", "docker", "git", "power bi", "spark"
    ],
}

# Cross-sector common skills (sprinkle)
COMMON_SKILLS = ["excel", "communication", "teamwork", "presentation", "data analysis"]

# Simple synonym mapping (canonical target)
SYNONYMS = {
    "ms excel": "excel",
    "microsoft excel": "excel",
    "analysis financiere": "financial analysis",
    "analyse financiere": "financial analysis",
    "controle interne": "internal control",
    "gestion de projet": "project management",
    "recherche marche": "market research",
    "apprentissage automatique": "machine learning",
    "ingenierie de donnees": "data engineering",
}

# A few bilingual variants (FR/EN mix)
FR_EN_VARIANTS = {
    "financial analysis": ["analyse financiere", "analysis financiere"],
    "internal control": ["controle interne"],
    "project management": ["gestion de projet"],
    "market research": ["recherche marche"],
    "machine learning": ["apprentissage automatique"],
    "data engineering": ["ingenierie de donnees"],
}

# Tiny typo generator (swap or drop one character)
def _make_typo(word: str) -> str:
    if len(word) < 4:
        return word
    w = list(word)
    # pick a letter position that is alnum
    idxs = [i for i, ch in enumerate(w) if ch.isalnum()]
    if not idxs:
        return word
    i = random.choice(idxs)
    if random.random() < 0.5 and i + 1 < len(w):
        w[i], w[i + 1] = w[i + 1], w[i]
        return "".join(w)
    # drop char
    del w[i]
    return "".join(w)


def _normalize_sector(s: str) -> str:
    s = str(s).strip().lower()
    return SECTOR_CANONICAL.get(s, s)


def _sample_sector(cfg: GenConfig) -> str:
    sectors = list(cfg.sector_probs.keys())
    probs = list(cfg.sector_probs.values())
    return random.choices(sectors, weights=probs, k=1)[0]


def _sample_education(cfg: GenConfig) -> str:
    return random.choices(cfg.education_levels, weights=cfg.education_probs, k=1)[0]


def _sample_languages(cfg: GenConfig, min_k: int = 1, max_k: int = 2) -> List[str]:
    k = random.randint(min_k, max_k)
    langs = list(np.random.choice(cfg.language_pool, size=k, replace=False, p=cfg.language_probs))
    return sorted(set(langs))


def _apply_noise_to_skills(skills: List[str], cfg: GenConfig) -> List[str]:
    out = []
    for sk in skills:
        s = sk

        # synonym substitution
        if random.random() < cfg.p_synonym_skill:
            # sometimes replace by synonym key (non-canonical), sometimes map to canonical from key
            if random.random() < 0.5 and s in FR_EN_VARIANTS:
                s = random.choice(FR_EN_VARIANTS[s])
            else:
                # pick a synonym that maps to same canonical if possible
                # (use key that maps to this canonical if exists)
                keys = [k for k, v in SYNONYMS.items() if v == s]
                if keys:
                    s = random.choice(keys)

        # FR/EN variants
        if random.random() < cfg.p_mix_fr_en_skill and s in FR_EN_VARIANTS:
            s = random.choice(FR_EN_VARIANTS[s])

        # typo (only if single token or small)
        if random.random() < cfg.p_typo_in_skill:
            s = _make_typo(s)

        out.append(s)

    # dedup keep order
    seen = set()
    deduped = []
    for s in out:
        s2 = str(s).strip().lower()
        if s2 and s2 not in seen:
            seen.add(s2)
            deduped.append(s2)
    return deduped


def _pick_skills_for_candidate(sector: str, cfg: GenConfig) -> List[str]:
    base = SKILLS_BY_SECTOR[sector]
    k = random.randint(cfg.min_skills, cfg.max_skills)
    # ensure some common skills show up sometimes
    mix = base + (COMMON_SKILLS * 2)
    skills = random.sample(mix, k=min(k, len(set(mix))))
    skills = [s.lower() for s in skills]
    return _apply_noise_to_skills(skills, cfg)


def _pick_skills_for_job(sector: str, cfg: GenConfig) -> List[str]:
    base = SKILLS_BY_SECTOR[sector]
    k = random.randint(cfg.min_req_skills, cfg.max_req_skills)
    mix = base + COMMON_SKILLS
    skills = random.sample(mix, k=min(k, len(set(mix))))
    skills = [s.lower() for s in skills]
    # job skills should be mostly canonical (less noise), but keep a tiny bit
    job_cfg = GenConfig(**{**cfg.__dict__, "p_typo_in_skill": cfg.p_typo_in_skill * 0.25,
                           "p_synonym_skill": cfg.p_synonym_skill * 0.25,
                           "p_mix_fr_en_skill": cfg.p_mix_fr_en_skill * 0.25})
    return _apply_noise_to_skills(skills, job_cfg)


def _sample_experience(cfg: GenConfig, sector: str) -> float:
    # slightly different distributions by sector
    if sector == "audit":
        # juniors heavy: 0-3 more frequent
        vals = np.random.choice(range(cfg.max_years_experience + 1), p=_exp_probs(cfg.max_years_experience, "junior"))
    elif sector == "consulting":
        vals = np.random.choice(range(cfg.max_years_experience + 1), p=_exp_probs(cfg.max_years_experience, "mixed"))
    else:
        vals = np.random.choice(range(cfg.max_years_experience + 1), p=_exp_probs(cfg.max_years_experience, "mixed"))
    return float(vals)


def _exp_probs(max_y: int, mode: str) -> np.ndarray:
    xs = np.arange(max_y + 1)
    if mode == "junior":
        # geometric-ish
        w = np.exp(-0.45 * xs)
    else:
        w = np.exp(-0.35 * xs)
    w = w / w.sum()
    return w


def _min_experience_for_job(cfg: GenConfig, sector: str) -> float:
    # jobs: more likely 0-2, sometimes 3-5
    if sector == "audit":
        choices = [0, 0, 0, 1, 1, 2, 2, 3, 4]
    elif sector == "consulting":
        choices = [0, 0, 1, 1, 2, 2, 3, 4]
    else:
        choices = [0, 0, 1, 2, 2, 3, 4, 5]
    return float(random.choice(choices))


def _required_education_for_job(cfg: GenConfig, sector: str) -> str:
    # mostly bac+5 for audit/consulting, mixed for IT/data
    if sector in ("audit", "consulting"):
        return random.choices(["bac+4", "bac+5"], weights=[0.15, 0.85], k=1)[0]
    return random.choices(["bac+3", "bac+4", "bac+5"], weights=[0.35, 0.15, 0.50], k=1)[0]


# -----------------------------
# Main generators
# -----------------------------
def generate_candidates(cfg: GenConfig) -> pd.DataFrame:
    rows = []
    for i in range(cfg.n_candidates):
        cid = f"C{i+1:06d}"

        sector = _sample_sector(cfg)
        if random.random() < cfg.p_missing_sector:
            sector_out = ""
        else:
            sector_out = sector

        edu = _sample_education(cfg)
        if random.random() < cfg.p_missing_education:
            edu_out = ""
        else:
            edu_out = edu

        years = _sample_experience(cfg, sector)

        langs = _sample_languages(cfg, min_k=1, max_k=2)
        if random.random() < cfg.p_missing_languages:
            langs_out = []
        else:
            langs_out = langs

        skills = _pick_skills_for_candidate(sector, cfg)

        rows.append({
            "candidate_id": cid,
            "candidate_skills": skills,        # list -> will be written as string in CSV, your preprocessing handles it
            "years_experience": years,
            "education_level": edu_out,
            "languages": langs_out,            # list
            "sector": sector_out,
        })

    return pd.DataFrame(rows)


def generate_jobs(cfg: GenConfig) -> pd.DataFrame:
    rows = []
    for j in range(cfg.n_jobs):
        jid = f"J{j+1:04d}"

        sector = _sample_sector(cfg)
        req_skills = _pick_skills_for_job(sector, cfg)

        min_exp = _min_experience_for_job(cfg, sector)
        req_edu = _required_education_for_job(cfg, sector)
        req_langs = _sample_languages(cfg, min_k=cfg.min_req_lang, max_k=cfg.max_req_lang)

        rows.append({
            "job_id": jid,
            "required_skills": req_skills,        # list
            "min_experience": min_exp,
            "required_education": req_edu,
            "required_languages": req_langs,      # list
            "required_sector": sector,
        })

    return pd.DataFrame(rows)


def _write_csv(df: pd.DataFrame, path: str) -> None:
    # Write lists as a python-like list string; your preprocessing can parse it.
    df_to_write = df.copy()
    for col in df_to_write.columns:
        if df_to_write[col].apply(lambda x: isinstance(x, list)).any():
            df_to_write[col] = df_to_write[col].apply(lambda x: str(x) if isinstance(x, list) else x)
    df_to_write.to_csv(path, index=False, encoding="utf-8")


def main() -> None:
    cfg = GenConfig()
    cfg.sector_probs = {"audit": 0.42, "consulting": 0.33, "it / data": 0.25}

    _set_seed(cfg.seed)
    _ensure_dirs(cfg.dev_dir, cfg.samples_dir)

    print(f"Generating DEV data: {cfg.n_candidates} candidates, {cfg.n_jobs} jobs ...")
    df_c = generate_candidates(cfg)
    df_j = generate_jobs(cfg)

    dev_c_path = os.path.join(cfg.dev_dir, "candidates_dev.csv")
    dev_j_path = os.path.join(cfg.dev_dir, "jobs_dev.csv")
    _write_csv(df_c, dev_c_path)
    _write_csv(df_j, dev_j_path)

    # Samples (small, versionable)
    df_c_s = df_c.sample(n=min(25, len(df_c)), random_state=cfg.seed).reset_index(drop=True)
    df_j_s = df_j.sample(n=min(10, len(df_j)), random_state=cfg.seed).reset_index(drop=True)

    samp_c_path = os.path.join(cfg.samples_dir, "candidates_sample.csv")
    samp_j_path = os.path.join(cfg.samples_dir, "jobs_sample.csv")
    _write_csv(df_c_s, samp_c_path)
    _write_csv(df_j_s, samp_j_path)

    print(f"Wrote: {dev_c_path}")
    print(f"Wrote: {dev_j_path}")
    print(f"Wrote: {samp_c_path}")
    print(f"Wrote: {samp_j_path}")
    print("Done.")


if __name__ == "__main__":
    main()

