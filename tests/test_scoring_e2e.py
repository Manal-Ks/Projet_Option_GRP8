import os
from scripts.run_scoring_experiments import generate_synthetic, main as run_main


def test_e2e_run(tmp_path, monkeypatch):
    # generate small dataset and run experiments writing to tmp path
    pairs = generate_synthetic(num_jobs=3, num_candidates=12, seed=1)
    # monkeypatch output dir by setting cwd
    cwd = os.getcwd()
    try:
        os.chdir(tmp_path)
        from src.scoring_engine.evaluation import run_experiments
        run_experiments(pairs, output_dir=str(tmp_path))
        assert (tmp_path / "leaderboard.csv").exists()
        assert (tmp_path / "best_algo_top10.csv").exists()
        assert (tmp_path / "config_used.json").exists()
    finally:
        os.chdir(cwd)
