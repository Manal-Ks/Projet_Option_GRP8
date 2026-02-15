import pandas as pd
from src.data_layer import prepare_data_layer

def test_prepare_data_layer_returns_pairs_and_reports():
    df_cv = pd.DataFrame([{
        "candidate_id": "1",
        "candidate_skills": "Audit, Excel",
        "years_experience": 1,
        "education_level": "Bac+5",
        "languages": "FR,EN",
        "sector": "Audit",
    }])
    df_jobs = pd.DataFrame([{
        "job_id": "A",
        "required_skills": "Audit, Excel",
        "min_experience": 0,
        "required_education": "Bac+5",
        "required_languages": "FR",
        "required_sector": "Audit",
    }])

    pairs, qc, qj = prepare_data_layer(df_cv, df_jobs, pairing_mode="cartesian")
    assert len(pairs) == 1
    assert "pct_empty_skills" in qc
    assert "pct_empty_required_skills" in qj
