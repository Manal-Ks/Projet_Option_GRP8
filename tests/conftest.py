"""
conftest.py - Fixture et configuration des tests pytest
Génère des données réalistes pour les tests
"""
import random
import pandas as pd
import numpy as np
import pytest
from typing import Tuple, List


class RealisticDataGenerator:
    """Génère des données d'embauche/candidats réalistes pour tester"""
    
    SECTORS = [
        "it_data", "finance", "marketing", "sales", "hr",
        "logistics", "manufacturing", "healthcare", "education", "retail"
    ]
    
    EDUCATION_LEVELS = {
        "bac": 1, "bac+2": 2, "bac+3": 3, "bac+5": 4, "doctorat": 5
    }
    
    SKILLS_POOL = [
        "python", "java", "javascript", "sql", "docker",
        "aws", "machine_learning", "analytics", "communication", "leadership",
        "project_management", "sales", "customer_service", "accounting", "design",
        "data_visualization", "excel", "powerpoint", "git", "agile"
    ]
    
    LANGUAGES = ["en", "fr", "es", "de", "it", "pt", "ja", "zh"]
    
    JOB_TITLES = [
        "Data Engineer", "Data Scientist", "Software Engineer",
        "Product Manager", "Sales Manager", "HR Manager",
        "Marketing Manager", "DevOps Engineer", "QA Engineer",
        "Financial Analyst", "Business Analyst"
    ]
    
    @staticmethod
    def generate_candidates(num_candidates: int, seed: int = 42) -> pd.DataFrame:
        """Génère des candidats réalistes"""
        random.seed(seed)
        np.random.seed(seed)
        
        candidates = []
        for i in range(num_candidates):
            years_exp = np.random.randint(0, 20)
            num_skills = np.random.randint(3, 10)
            
            candidate = {
                "candidate_id": f"cand_{i+1:05d}",
                "name": f"Candidate_{i+1}",
                "years_experience": years_exp,
                "education_level": random.choice(list(RealisticDataGenerator.EDUCATION_LEVELS.keys())),
                "education_level_num": random.choice(list(RealisticDataGenerator.EDUCATION_LEVELS.values())),
                "candidate_sector": random.choice(RealisticDataGenerator.SECTORS),
                "skills": random.sample(RealisticDataGenerator.SKILLS_POOL, num_skills),
                "languages": random.sample(RealisticDataGenerator.LANGUAGES, random.randint(1, 3)),
                "location": f"City_{random.randint(1, 50)}",
            }
            candidates.append(candidate)
        
        return pd.DataFrame(candidates)
    
    @staticmethod
    def generate_jobs(num_jobs: int, seed: int = 42) -> pd.DataFrame:
        """Génère des offres d'emploi réalistes"""
        random.seed(seed)
        np.random.seed(seed)
        
        jobs = []
        for i in range(num_jobs):
            min_exp = np.random.randint(0, 10)
            min_edu = random.choice(list(RealisticDataGenerator.EDUCATION_LEVELS.values()))
            num_skills = np.random.randint(3, 8)
            
            job = {
                "job_id": f"job_{i+1:05d}",
                "title": random.choice(RealisticDataGenerator.JOB_TITLES),
                "required_sector": random.choice(RealisticDataGenerator.SECTORS),
                "min_experience": min_exp,
                "required_education": random.choice(list(RealisticDataGenerator.EDUCATION_LEVELS.keys())),
                "required_education_num": min_edu,
                "required_skills": random.sample(RealisticDataGenerator.SKILLS_POOL, num_skills),
                "required_languages": random.sample(RealisticDataGenerator.LANGUAGES, random.randint(1, 2)),
                "salary_min": random.randint(30000, 120000),
                "salary_max": random.randint(50000, 180000),
                "location": f"City_{random.randint(1, 50)}",
            }
            jobs.append(job)
        
        return pd.DataFrame(jobs)
    
    @staticmethod
    def generate_realistic_dataset(
        num_candidates: int = 100,
        num_jobs: int = 20,
        seed: int = 42
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Génère un dataset candidats + jobs réaliste"""
        candidates = RealisticDataGenerator.generate_candidates(num_candidates, seed)
        jobs = RealisticDataGenerator.generate_jobs(num_jobs, seed + 1)
        return candidates, jobs
    
    @staticmethod
    def generate_edge_case_dataset() -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Génère un dataset avec cas limites pour tester"""
        # Candidat avec 0 compétence, 0 expérience, pas de langue, etc.
        candidates = pd.DataFrame([
            {
                "candidate_id": "edge_1",
                "name": "Edge Case 1",
                "years_experience": 0,
                "education_level": "bac",
                "education_level_num": 1,
                "candidate_sector": "it_data",
                "skills": [],
                "languages": [],
                "location": "Unknown",
            },
            # Candidat sur-qualifié
            {
                "candidate_id": "edge_2",
                "name": "Overqualified",
                "years_experience": 25,
                "education_level": "doctorat",
                "education_level_num": 5,
                "candidate_sector": "it_data",
                "skills": RealisticDataGenerator.SKILLS_POOL[:15],
                "languages": RealisticDataGenerator.LANGUAGES,
                "location": "Paris",
            },
            # Candidat avec différents secteurs
            {
                "candidate_id": "edge_3",
                "name": "Different Sector",
                "years_experience": 5,
                "education_level": "bac+3",
                "education_level_num": 3,
                "candidate_sector": "healthcare",
                "skills": ["communication", "leadership"],
                "languages": ["fr"],
                "location": "Lyon",
            },
        ])
        
        jobs = pd.DataFrame([
            # Poste très sélectif
            {
                "job_id": "edge_job_1",
                "title": "Senior Data Scientist",
                "required_sector": "it_data",
                "min_experience": 10,
                "required_education": "doctorat",
                "required_education_num": 5,
                "required_skills": ["machine_learning", "python", "sql", "aws"],
                "required_languages": ["en", "fr"],
                "salary_min": 80000,
                "salary_max": 150000,
                "location": "Paris",
            },
            # Poste débutant
            {
                "job_id": "edge_job_2",
                "title": "Junior Developer",
                "required_sector": "it_data",
                "min_experience": 0,
                "required_education": "bac+2",
                "required_education_num": 2,
                "required_skills": ["javascript"],
                "required_languages": ["en"],
                "salary_min": 25000,
                "salary_max": 35000,
                "location": "Remote",
            },
        ])
        
        return candidates, jobs


# Fixtures pytest

@pytest.fixture
def realistic_candidates():
    """Fixture : dataset de candidats réalistes"""
    return RealisticDataGenerator.generate_candidates(50, seed=42)


@pytest.fixture
def realistic_jobs():
    """Fixture : dataset d'offres réalistes"""
    return RealisticDataGenerator.generate_jobs(10, seed=42)


@pytest.fixture
def realistic_dataset():
    """Fixture : dataset complet candidats + jobs"""
    return RealisticDataGenerator.generate_realistic_dataset(50, 10, seed=42)


@pytest.fixture
def edge_case_dataset():
    """Fixture : dataset avec cas limites"""
    return RealisticDataGenerator.generate_edge_case_dataset()


@pytest.fixture
def small_dataset():
    """Fixture : petit dataset pour tests rapides"""
    return RealisticDataGenerator.generate_realistic_dataset(10, 3, seed=42)


@pytest.fixture
def large_dataset():
    """Fixture : grand dataset pour benchmarks"""
    return RealisticDataGenerator.generate_realistic_dataset(10000, 100, seed=42)
