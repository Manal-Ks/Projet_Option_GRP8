# demo_dev_run.py
# Run from repo root:
#   python demo_dev_run.py
#
# It will prefer DEV data if present, otherwise uses samples.

from __future__ import annotations
import os
import pandas as pd

# If your modules are in src/, ensure src is on sys.path
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from data_layer import prepare_data_layer  # noqa: E402


def _read_csv(path: str) -> pd.DataFrame:
    return pd.read_csv(path, encoding="utf-8")


def main() -> None:
    dev_c = "data/dev/candidates_dev.csv"
    dev_j = "data/dev/jobs_dev.csv"
    samp_c = "data/samples/candidates_sample.csv"
    samp_j = "data/samples/jobs_sample.csv"

    if os.path.exists(dev_c) and os.path.exists(dev_j):
        c_path, j_path = dev_c, dev_j
        print("Using DEV dataset.")
    else:
        c_path, j_path = samp_c, samp_j
        print("DEV dataset not found. Using SAMPLES dataset.")

    df_c = _read_csv(c_path)
    df_j = _read_csv(j_path)

    pairs, qc, qj = prepare_data_layer(df_c, df_j, pairing_mode="cartesian")

    print("\n--- Counts ---")
    print(f"candidates: {len(df_c)}")
    print(f"jobs      : {len(df_j)}")
    print(f"pairs     : {len(pairs)}")

    print("\n--- Quality report (candidates) ---")
    for k, v in qc.items():
        print(f"{k}: {v}")

    print("\n--- Quality report (jobs) ---")
    for k, v in qj.items():
        print(f"{k}: {v}")

    print("\n--- Sample pairs ---")
    cols = ["candidate_id", "job_id", "sector", "required_sector", "candidate_skills", "required_skills"]
    cols = [c for c in cols if c in pairs.columns]
    print(pairs[cols].head(3))


if __name__ == "__main__":
    main()

