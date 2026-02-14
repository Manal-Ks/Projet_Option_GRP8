import pandas as pd

from schema import validate_and_coerce, CANDIDATE_SCHEMA, JOB_SCHEMA
from preprocessing import preprocess_candidates, preprocess_jobs
from pairing import build_pairs_cartesian

def main():
    # --- Example dummy data (replace with your real fictive dataset later)
    df_cv = pd.DataFrame([
        {
            "candidate_id": "1",
            "candidate_skills": "Audit; Excel, IFRS",
            "years_experience": "2",
            "education_level": "Bac+5",
            "languages": "FR|EN",
            "sector": "Audit",
        },
        {
            "candidate_id": "2",
            "candidate_skills": "Python, Data; Excel",
            "years_experience": 0,
            "education_level": "Bac+3",
            "languages": ["FR"],
            "sector": "IT / Data",
        },
    ])

    df_jobs = pd.DataFrame([
        {
            "job_id": "A",
            "required_skills": "audit, excel",
            "min_experience": 0,
            "required_education": "bac+5",
            "required_languages": "fr,en",
            "required_sector": "audit",
        },
        {
            "job_id": "B",
            "required_skills": ["python", "excel"],
            "min_experience": 1,
            "required_education": "bac+3",
            "required_languages": ["fr"],
            "required_sector": "it / data",
        },
    ])

    # 1) Validate & coerce
    df_cv = validate_and_coerce(df_cv, CANDIDATE_SCHEMA, "candidates")
    df_jobs = validate_and_coerce(df_jobs, JOB_SCHEMA, "jobs")

    # 2) Preprocess
    df_cv = preprocess_candidates(df_cv)
    df_jobs = preprocess_jobs(df_jobs)

    # 3) Pairing
    df_pairs = build_pairs_cartesian(df_cv, df_jobs)

    print("\n--- Preprocessed candidates ---")
    print(df_cv)

    print("\n--- Preprocessed jobs ---")
    print(df_jobs)

    print("\n--- Pairs (candidate-job) ---")
    print(df_pairs[["candidate_id", "job_id", "candidate_skills", "required_skills"]])

if __name__ == "__main__":
    main()

