"""Run scoring experiments: generate small synthetic dataset, run algorithms, save results."""
from __future__ import annotations
import os
import sys
import json
import numpy as np
import pandas as pd

# Add parent directory to path so src modules can be imported
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.scoring_engine.evaluation import run_experiments, compute_subscores_df


def generate_synthetic(num_jobs=5, num_candidates=30, seed=42):
    rng = np.random.RandomState(seed)
    jobs = []
    for j in range(num_jobs):
        jobs.append({
            "job_id": f"J{j:03d}",
            "required_skills": ["excel"] if j % 2 == 0 else ["machine_learning"],
            "required_languages": ["en", "fr"] if j % 2 == 0 else ["en"],
            "required_education_num": 5 if j % 3 == 0 else 3,
            "required_sector": "it_data" if j % 2 == 0 else "consulting",
            "min_experience": 2 + (j % 3),
        })

    cands = []
    for i in range(num_candidates):
        cands.append({
            "candidate_id": f"C{i:04d}",
            "candidate_skills": ["excel"] if i % 2 == 0 else ["machine_learning"],
            "languages": ["en"] if i % 3 == 0 else ["en", "fr"],
            "education_level_num": 5 if i % 5 == 0 else 3,
            "sector": "it_data" if i % 2 == 0 else "consulting",
            "years_experience": float(i % 6),
        })

    df_jobs = pd.DataFrame(jobs)
    df_cands = pd.DataFrame(cands)
    df_cands["_key"] = 1
    df_jobs["_key"] = 1
    pairs = df_cands.merge(df_jobs, on="_key", how="inner").drop(columns=["_key"])
    pairs = compute_subscores_df(pairs)
    # label: weighted sum + noise
    pairs["label"] = (
        0.4 * pairs["score_skills"] +
        0.3 * pairs["score_experience"] +
        0.2 * pairs["score_education"] +
        0.1 * pairs["score_languages"]
    )
    pairs["label"] = (pairs["label"] + rng.normal(0, 0.05, size=len(pairs))).clip(0.0, 1.0)
    return pairs


def main():
    os.makedirs("results", exist_ok=True)
    pairs = generate_synthetic()
    run_experiments(pairs, output_dir="results")
    print("Experiments finished. Results in results/")


if __name__ == "__main__":
    main()
