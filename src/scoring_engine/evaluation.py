from __future__ import annotations
import os
import json
import time
import numpy as np
import pandas as pd
from typing import Tuple, Dict
from sklearn.model_selection import train_test_split

from .config import SEEDS, K, DEFAULT_WEIGHTS
from .components.subscores import (
    skills_jaccard,
    experience_score,
    education_score,
    languages_score,
    sector_score,
)
from .algorithms.algorithms import (
    WSMAlgorithm,
    WPMAlgorithm,
    TOPSISAlgorithm,
    LogisticRegressionAlgorithm,
    GradientBoostingAlgorithm,
    RandomForestAlgorithm,
)
from .metrics.ranking_metrics import precision_at_k, recall_at_k, ndcg_at_k, map_at_k, mrr_at_k


def split_by_candidate_id(df: pd.DataFrame, test_size=0.3, seed=42) -> Tuple[pd.DataFrame, pd.DataFrame]:
    cids = df["candidate_id"].unique()
    train_ids, test_ids = train_test_split(cids, test_size=test_size, random_state=seed)
    train = df[df["candidate_id"].isin(train_ids)].reset_index(drop=True)
    test = df[df["candidate_id"].isin(test_ids)].reset_index(drop=True)
    return train, test


def compute_subscores_df(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["score_skills"] = out.apply(lambda r: skills_jaccard(r.get("candidate_skills"), r.get("required_skills")), axis=1)
    out["score_experience"] = out.apply(lambda r: experience_score(r.get("years_experience"), r.get("min_experience")), axis=1)
    out["score_education"] = out.apply(lambda r: education_score(r.get("education_level_num"), r.get("required_education_num")), axis=1)
    out["score_languages"] = out.apply(lambda r: languages_score(r.get("languages"), r.get("required_languages")), axis=1)
    out["score_sector"] = out.apply(lambda r: sector_score(r.get("sector"), r.get("required_sector")), axis=1)
    for c in ["score_skills", "score_experience", "score_education", "score_languages", "score_sector"]:
        out[c] = out[c].fillna(0.0).astype(float).clip(0.0, 1.0)
    return out


def run_algorithm_and_eval(alg, train_df, test_df, label_col="label") -> Dict[str, float]:
    result = {}
    # prepare labels for ML
    y_train = (train_df[label_col] >= 0.5).astype(int) if label_col in train_df else None

    start = time.time()
    try:
        alg.fit(train_df, y_train)
    except Exception:
        pass
    preds = alg.predict(test_df)
    runtime = time.time() - start

    # evaluate per job
    jobs = test_df["job_id"].unique()
    metrics = {"precision": [], "recall": [], "ndcg": [], "map": [], "mrr": []}
    for jid in jobs:
        subset = test_df[test_df["job_id"] == jid]
        if subset.empty:
            continue
        y_true = subset[label_col].values if label_col in subset else np.zeros(len(subset))
        scores = preds[subset.index]
        metrics["precision"].append(precision_at_k(y_true, scores, k=K))
        metrics["recall"].append(recall_at_k(y_true, scores, k=K))
        metrics["ndcg"].append(ndcg_at_k(y_true, scores, k=K))
        metrics["map"].append(map_at_k(y_true, scores, k=K))
        metrics["mrr"].append(mrr_at_k(y_true, scores, k=K))

    # aggregate
    result = {
        "precision@k": float(np.mean(metrics["precision"])) if metrics["precision"] else 0.0,
        "recall@k": float(np.mean(metrics["recall"])) if metrics["recall"] else 0.0,
        "ndcg@k": float(np.mean(metrics["ndcg"])) if metrics["ndcg"] else 0.0,
        "map@k": float(np.mean(metrics["map"])) if metrics["map"] else 0.0,
        "mrr@k": float(np.mean(metrics["mrr"])) if metrics["mrr"] else 0.0,
        "runtime": float(runtime),
    }
    return result


def run_experiments(df_pairs: pd.DataFrame, output_dir: str = "results") -> None:
    os.makedirs(output_dir, exist_ok=True)
    df = compute_subscores_df(df_pairs)

    algos = {
        "WSM": WSMAlgorithm(),
        "WPM": WPMAlgorithm(),
        "TOPSIS": TOPSISAlgorithm(),
        "LogisticRegression": LogisticRegressionAlgorithm(),
        "GradientBoosting": GradientBoostingAlgorithm(),
        "RandomForest": RandomForestAlgorithm(),
    }

    records = []
    best_algo = None
    best_ndcg = -1.0

    for seed in SEEDS:
        train, test = split_by_candidate_id(df, seed=seed)
        for name, alg in algos.items():
            res = run_algorithm_and_eval(alg, train, test, label_col="label")
            res["algo"] = name
            res["seed"] = seed
            records.append(res)

    df_res = pd.DataFrame(records)
    # leaderboard mean and std
    leaderboard = df_res.groupby("algo").agg({
        "precision@k": ["mean", "std"],
        "recall@k": ["mean", "std"],
        "ndcg@k": ["mean", "std"],
        "map@k": ["mean", "std"],
        "mrr@k": ["mean", "std"],
        "runtime": ["mean", "std"],
    })
    leaderboard.to_csv(os.path.join(output_dir, "leaderboard.csv"))

    # choose best by ndcg mean
    ndcg_means = leaderboard[('ndcg@k', 'mean')]
    best_algo = ndcg_means.idxmax()

    # compute top10 for best algo on full df
    best = algos.get(best_algo, list(algos.values())[0])
    try:
        best.fit(df, (df["label"] >= 0.5).astype(int))
    except Exception:
        pass
    scores = best.predict(df)
    df_scores = df.copy()
    df_scores["score"] = scores
    # example job: first job id
    job0 = df_scores["job_id"].unique()[0]
    top10 = df_scores[df_scores["job_id"] == job0].sort_values("score", ascending=False).head(10)
    top10[["candidate_id", "job_id", "score"]].to_csv(os.path.join(output_dir, "best_algo_top10.csv"), index=False)

    # save config used
    with open(os.path.join(output_dir, "config_used.json"), "w", encoding="utf-8") as fh:
        json.dump({"weights": DEFAULT_WEIGHTS, "seeds": SEEDS, "k": K, "best_algo": best_algo}, fh, indent=2)
