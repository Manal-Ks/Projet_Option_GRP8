import pandas as pd

from src.preprocessing import preprocess_candidates, preprocess_jobs


def test_candidate_and_job_normalizers():
    df_c = pd.DataFrame([
        {
            "candidate_id": "c1",
            "candidate_skills": "['ms excel','machine learning']",
            "languages": "['FR','EN']",
            "education_level": "bac+5",
            "sector": "IT/Data",
            "years_experience": 2,
        }
    ])

    df_j = pd.DataFrame([
        {
            "job_id": "j1",
            "required_skills": "['ms excel','machine learning']",
            "required_languages": "['EN','FR']",
            "required_education": "bac+5",
            "required_sector": "IT/Data",
            "min_experience": 1,
        }
    ])

    pc = preprocess_candidates(df_c)
    pj = preprocess_jobs(df_j)

    # candidates
    assert pc.loc[0, "education_level_num"] == 5
    assert pc.loc[0, "languages"] == ["en", "fr"]
    skills = pc.loc[0, "candidate_skills"]
    assert "excel" in skills
    assert "machine_learning" in skills
    assert pc.loc[0, "sector"] == "it_data"

    # jobs
    assert pj.loc[0, "required_education_num"] == 5
    assert pj.loc[0, "required_languages"] == ["en", "fr"]
    jskills = pj.loc[0, "required_skills"]
    assert "excel" in jskills
    assert "machine_learning" in jskills
    assert pj.loc[0, "required_sector"] == "it_data"
