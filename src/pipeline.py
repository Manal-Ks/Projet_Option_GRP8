# src/pipeline.py
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Tuple

import pandas as pd
import yaml
import numpy as np

from src.data_layer import prepare_data_layer
from src.aggregate import WeightConfig, make_vector_score, select_output_columns, weighted_global_score
from src.export import export_csv, export_json

# IMPORTANT:
# adapte l'import suivant selon ton fichier réel (le README dit: src/scoring_engine/components/subscores.py)
from src.scoring_engine.components.subscores import compute_subscores  # doit retourner df avec score_* colonnes
from src.scoring_engine.algorithms.algorithms import (
    WSMAlgorithm,
    WPMAlgorithm,
    TOPSISAlgorithm,
    LogisticRegressionAlgorithm,
    GradientBoostingAlgorithm,
    RandomForestAlgorithm,
)
from src.scoring_engine.config import DEFAULT_WEIGHTS


@dataclass
class PipelineConfig:
    pairing_mode: str = "cartesian"
    batch_size: int = 200000
    export_dir: str = "results"
    export_format: List[str] = None
    keep_columns: List[str] = None

    scoring_mode: str = "weighted_subscores"  # ou "algo"
    algo_name: str = "TOPSIS"
    weights: WeightConfig = WeightConfig()

    @staticmethod
    def from_yaml(path: str | Path) -> "PipelineConfig":
        path = Path(path)
        with open(path, "r", encoding="utf-8") as f:
            raw = yaml.safe_load(f) or {}

        p = raw.get("pipeline", {})
        s = raw.get("scoring", {})

        weights_raw = s.get("weights", {}) or {}
        w = WeightConfig(
            skills=float(weights_raw.get("skills", 0.35)),
            experience=float(weights_raw.get("experience", 0.20)),
            education=float(weights_raw.get("education", 0.15)),
            languages=float(weights_raw.get("languages", 0.15)),
            sector=float(weights_raw.get("sector", 0.15)),
        )

        return PipelineConfig(
            pairing_mode=str(p.get("pairing_mode", "cartesian")),
            batch_size=int(p.get("batch_size", 200000)),
            export_dir=str(p.get("export_dir", "results")),
            export_format=list(p.get("export_format", ["csv"])),
            keep_columns=list(p.get("keep_columns", [])),
            scoring_mode=str(s.get("mode", "weighted_subscores")),
            algo_name=str(s.get("algo_name", "TOPSIS")),
            weights=w,
        )


def _score_in_batches(pairs: pd.DataFrame, batch_size: int) -> pd.DataFrame:
    if len(pairs) <= batch_size:
        return compute_subscores(pairs)

    chunks = []
    for start in range(0, len(pairs), batch_size):
        end = min(start + batch_size, len(pairs))
        chunk = pairs.iloc[start:end].copy()
        chunks.append(compute_subscores(chunk))
    return pd.concat(chunks, ignore_index=True)


def _get_algorithm(algo_name: str, weights: Dict = None):
    """
    Crée une instance de l'algorithme choisi.
    
    Args:
        algo_name: Nom de l'algorithme (WSM, WPM, TOPSIS, LogisticRegression, GradientBoosting, RandomForest)
        weights: Dict de poids pour les algorithmes non-ML
        
    Returns:
        Instance de l'algorithme
    """
    w = weights or DEFAULT_WEIGHTS
    algos = {
        "WSM": WSMAlgorithm(w),
        "WPM": WPMAlgorithm(w),
        "TOPSIS": TOPSISAlgorithm(w),
        "LogisticRegression": LogisticRegressionAlgorithm(),
        "GradientBoosting": GradientBoostingAlgorithm(),
        "RandomForest": RandomForestAlgorithm(),
    }
    return algos.get(algo_name, TOPSISAlgorithm(w))


def _apply_algorithm_scoring(df: pd.DataFrame, algo_name: str, weights: Dict = None) -> np.ndarray:
    """
    Applique l'algorithme choisi pour scorer les paires.
    
    Args:
        df: DataFrame avec subscores (score_skills, score_experience, etc.)
        algo_name: Nom de l'algorithme
        weights: Dict de poids
        
    Returns:
        Array de scores
    """
    algo = _get_algorithm(algo_name, weights)
    
    # Pour les algorithmes non-ML (WSM, WPM, TOPSIS), on appelle directement predict
    # Pour les algorithmes ML, il faut les entraîner d'abord
    if algo_name in ["LogisticRegression", "GradientBoosting", "RandomForest"]:
        # Si on n'a pas de labels, on entraîne sur toutes les données
        # C'est un workaround pour la prédiction sans ensemble d'entraînement
        y_dummy = np.zeros(len(df))
        algo.fit(df, y_dummy)
    
    return algo.predict(df)


def run(
    df_cv: pd.DataFrame,
    df_jobs: pd.DataFrame,
    config_path: str | Path = "config.yaml",
    export: bool = True,
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    API simple demandée: run(df_cv, df_jobs)
    Retour:
      - result_df : paires + subscores + global_score + vector_score
      - meta      : quality_report + chemins exports éventuels
    """
    cfg = PipelineConfig.from_yaml(config_path)

    # 1) data layer (validation + preprocess + pairing + quality)
    pairs, qc_candidates, qc_jobs = prepare_data_layer(
        df_cv,
        df_jobs,
        pairing_mode=cfg.pairing_mode,
    )

    quality_report = {
        "candidates": qc_candidates,
        "jobs": qc_jobs
    }

    # 2) subscores (skills/exp/edu/lang/sector)
    scored = _score_in_batches(pairs, cfg.batch_size)

    # 3) scoring: soit algorithme, soit somme pondérée
    if cfg.scoring_mode == "algo":
        # Appliquer l'algorithme choisi
        weights_dict = {
            "score_skills": cfg.weights.skills,
            "score_experience": cfg.weights.experience,
            "score_education": cfg.weights.education,
            "score_languages": cfg.weights.languages,
            "score_sector": cfg.weights.sector,
        }
        algo_scores = _apply_algorithm_scoring(scored, cfg.algo_name, weights_dict)
        scored["global_score"] = np.clip(algo_scores, 0.0, 1.0)
    else:
        # Mode par défaut: somme pondérée
        scored = make_vector_score(scored)
        scored = weighted_global_score(scored, cfg.weights)

    # 4) select output columns
    out = select_output_columns(scored, cfg.keep_columns)

    # 5) export
    meta: Dict[str, Any] = {"quality_report": quality_report, "exports": {}, "scoring_mode": cfg.scoring_mode, "algo_used": cfg.algo_name if cfg.scoring_mode == "algo" else None}
    if export:
        export_dir = Path(cfg.export_dir)
        if "csv" in (cfg.export_format or []):
            meta["exports"]["csv"] = str(export_csv(out, export_dir / "pairs_scored.csv"))
        if "json" in (cfg.export_format or []):
            meta["exports"]["json"] = str(export_json(out, export_dir / "pairs_scored.json"))

    return out, meta
