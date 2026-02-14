import pandas as pd
from ats_scoring.schema import validate_and_coerce, CANDIDATE_SCHEMA, JOB_SCHEMA
from ats_scoring.preprocessing import preprocess_candidates, preprocess_jobs
from ats_scoring.pairing import build_pairs_cartesian

def test_schema_and_preprocess():
    df_cv = pd.DataFrame([{
        "candidate_id": "1",
        "candidate_skills": "Audit; Excel, IFRS",
        "years_experience": "2",
        "education_level": "Bac+5",
        "languages": "FR|EN",
        "sector": "Audit",
    }])

    df_job = pd.DataFrame([{
        "job_id": "A",
        "required_skills": ["audit", "excel"],
        "min_experience": 0,
        "required_education": "bac+5",
        "required_languages": "fr,en",
        "required_sector": "audit",
    }])

    df_cv = validate_and_coerce(df_cv, CANDIDATE_SCHEMA, "candidates")
    df_job = validate_and_coerce(df_job, JOB_SCHEMA, "jobs")

    df_cv2 = preprocess_candidates(df_cv)
    df_job2 = preprocess_jobs(df_job)

    assert isinstance(df_cv2.loc[0, "candidate_skills"], list)
    assert "audit" in df_cv2.loc[0, "candidate_skills"]
    assert df_cv2.loc[0, "years_experience"] == 2.0
    assert "fr" in df_job2.loc[0, "required_languages"]

def test_pairing_cartesian_shape():
    df_cv = pd.DataFrame([{
        "candidate_id": "1",
        "candidate_skills": [],
        "years_experience": 0,
        "education_level": "",
        "languages": [],
        "sector": "",
    },{
        "candidate_id": "2",
        "candidate_skills": [],
        "years_experience": 0,
        "education_level": "",
        "languages": [],
        "sector": "",
    }])

    df_job = pd.DataFrame([{
        "job_id": "A",
        "required_skills": [],
        "min_experience": 0,
        "required_education": "",
        "required_languages": [],
        "required_sector": "",
    },{
        "job_id": "B",
        "required_skills": [],
        "min_experience": 0,
        "required_education": "",
        "required_languages": [],
        "required_sector": "",
    },{
        "job_id": "C",
        "required_skills": [],
        "min_experience": 0,
        "required_education": "",
        "required_languages": [],
        "required_sector": "",
    }])

    pairs = build_pairs_cartesian(df_cv, df_job)
    assert len(pairs) == 6
    assert "candidate_id" in pairs.columns and "job_id" in pairs.columns

