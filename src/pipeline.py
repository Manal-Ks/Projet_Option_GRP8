# src/pipeline.py
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Tuple

import pandas as pd
import yaml

from src.data_layer import prepare_data_layer
from src.aggregate import WeightConfig, make_vector_score, select_output_columns, weighted_global_score
from src.export import export_csv, export_json

# IMPORTANT:
# adapte l'import suivant selon ton fichier réel (le README dit: src/scoring_engine/components/subscores.py)
from src.scoring_engine.components.subscores import compute_subscores  # doit retourner df avec score_* colonnes


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

    # 3) aggregate
    scored = make_vector_score(scored)
    scored = weighted_global_score(scored, cfg.weights)
    out = select_output_columns(scored, cfg.keep_columns)

    # 4) export
    meta: Dict[str, Any] = {"quality_report": quality_report, "exports": {}}
    if export:
        export_dir = Path(cfg.export_dir)
        if "csv" in (cfg.export_format or []):
            meta["exports"]["csv"] = str(export_csv(out, export_dir / "pairs_scored.csv"))
        if "json" in (cfg.export_format or []):
            meta["exports"]["json"] = str(export_json(out, export_dir / "pairs_scored.json"))

    return out, meta
