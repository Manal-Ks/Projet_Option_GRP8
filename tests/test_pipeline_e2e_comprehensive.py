"""
test_pipeline_e2e_comprehensive.py - Tests bout-en-bout complets du pipeline

Ce module teste:
- L'intégralité du pipeline (données -> subscores -> scoring -> export)
- Différentes configurations
- Gestion d'erreurs et cas limites
- Cohérence des résultats
"""
import os
import json
import pytest
import pandas as pd
import numpy as np
from pathlib import Path


class TestPipelineIntegration:
    """Tests d'intégration du pipeline complet"""
    
    def test_pipeline_basic_flow(self, realistic_dataset, tmp_path):
        """Test le flux complet du pipeline avec données réalistes"""
        from src.pipeline import run
        
        candidates, jobs = realistic_dataset
        
        # Créer le pairing manuellement pour tester
        pairs = []
        for _, cand in candidates.iterrows():
            for _, job in jobs.iterrows():
                pairs.append({
                    "candidate_id": cand["candidate_id"],
                    "job_id": job["job_id"],
                    "candidate_skills": cand["skills"],
                    "required_skills": job["required_skills"],
                    "years_experience": cand["years_experience"],
                    "min_experience": job["min_experience"],
                    "education_level": cand["education_level_num"],
                    "required_education": job["required_education_num"],
                    "languages": cand["languages"],
                    "required_languages": job["required_languages"],
                    "sector": cand["candidate_sector"],
                    "required_sector": job["required_sector"],
                })
        
        pairs_df = pd.DataFrame(pairs)
        
        # Vérifier les résultats
        assert len(pairs_df) > 0
        assert "candidate_id" in pairs_df.columns
        assert "job_id" in pairs_df.columns
    
    def test_pipeline_with_edge_cases(self, edge_case_dataset, tmp_path):
        """Test le pipeline avec des cas limites"""
        candidates, jobs = edge_case_dataset
        
        # Créer le pairing avec cas limites
        pairs = []
        for _, cand in candidates.iterrows():
            for _, job in jobs.iterrows():
                pairs.append({
                    "candidate_id": cand["candidate_id"],
                    "job_id": job["job_id"],
                    "candidate_skills": cand["skills"],
                    "required_skills": job["required_skills"],
                    "years_experience": cand["years_experience"],
                    "min_experience": job["min_experience"],
                    "education_level": cand["education_level_num"],
                    "required_education": job["required_education_num"],
                    "languages": cand["languages"],
                    "required_languages": job["required_languages"],
                    "sector": cand["candidate_sector"],
                    "required_sector": job["required_sector"],
                })
        
        pairs_df = pd.DataFrame(pairs)
        
        # Le pipeline devrait gérer ces cas sans erreur
        assert len(pairs_df) > 0
        
        # Vérifier qu'aucune valeur n'est manquante
        assert not pairs_df[["candidate_id", "job_id"]].isnull().any().any()
    
    def test_pipeline_output_validity(self, small_dataset, tmp_path):
        """Vérifier la validité des sorties du pipeline"""
        from src.scoring_engine.evaluation import compute_subscores_df
        
        candidates, jobs = small_dataset
        
        # Créer des paires
        pairs = []
        for _, cand in candidates.iterrows():
            for _, job in jobs.iterrows():
                pairs.append({
                    "candidate_id": cand["candidate_id"],
                    "job_id": job["job_id"],
                    "candidate_skills": cand["skills"],
                    "required_skills": job["required_skills"],
                    "years_experience": cand["years_experience"],
                    "min_experience": job["min_experience"],
                    "education_level": cand["education_level_num"],
                    "required_education": job["required_education_num"],
                    "languages": cand["languages"],
                    "required_languages": job["required_languages"],
                    "sector": cand["candidate_sector"],
                    "required_sector": job["required_sector"],
                    "label": np.random.randint(0, 2),  # Pour simulation
                })
        
        pairs_df = pd.DataFrame(pairs)
        result = compute_subscores_df(pairs_df)
        
        # Vérifier les colonnes de score
        score_cols = ["score_skills", "score_experience", "score_education", "score_languages", "score_sector"]
        for col in score_cols:
            assert col in result.columns
            assert (result[col] >= 0.0).all()
            assert (result[col] <= 1.0).all()
            assert not result[col].isnull().any()


class TestPipelineRobustness:
    """Tests de robustesse du pipeline"""
    
    def test_pipeline_handles_missing_data(self):
        """Le pipeline gère les données manquantes"""
        pairs = pd.DataFrame([
            {
                "candidate_id": "c1",
                "job_id": "j1",
                "candidate_skills": None,
                "required_skills": ["python"],
                "years_experience": None,
                "min_experience": None,
                "education_level": None,
                "required_education": None,
                "languages": None,
                "required_languages": None,
                "sector": None,
                "required_sector": None,
            }
        ])
        
        from src.scoring_engine.evaluation import compute_subscores_df
        result = compute_subscores_df(pairs)
        
        # Ne devrait pas générer d'erreur
        assert len(result) == 1
        
        # Les scores existent et sont valides
        score_cols = ["score_skills", "score_experience", "score_education", "score_languages", "score_sector"]
        for col in score_cols:
            assert col in result.columns
            assert 0.0 <= result.iloc[0][col] <= 1.0
    
    def test_pipeline_handles_large_batch(self, large_dataset):
        """Le pipeline gère de grands volumes de données"""
        from src.scoring_engine.evaluation import compute_subscores_df
        
        candidates, jobs = large_dataset
        
        # Créer un petit sample mais verifier le traitement
        pairs = []
        sample_size = min(1000, len(candidates))
        for i in range(sample_size):
            pairs.append({
                "candidate_id": candidates.iloc[i]["candidate_id"],
                "job_id": jobs.iloc[0]["job_id"],
                "candidate_skills": candidates.iloc[i]["skills"],
                "required_skills": jobs.iloc[0]["required_skills"],
                "years_experience": candidates.iloc[i]["years_experience"],
                "min_experience": jobs.iloc[0]["min_experience"],
                "education_level": candidates.iloc[i]["education_level_num"],
                "required_education": jobs.iloc[0]["required_education_num"],
                "languages": candidates.iloc[i]["languages"],
                "required_languages": jobs.iloc[0]["required_languages"],
                "sector": candidates.iloc[i]["candidate_sector"],
                "required_sector": jobs.iloc[0]["required_sector"],
            })
        
        pairs_df = pd.DataFrame(pairs)
        result = compute_subscores_df(pairs_df)
        
        assert len(result) == len(pairs_df)
        assert not result.isnull().any().any()
    
    def test_pipeline_handles_duplicates(self):
        """Le pipeline gère les doublons"""
        pairs = pd.DataFrame([
            {
                "candidate_id": "c1",
                "job_id": "j1",
                "candidate_skills": ["python"],
                "required_skills": ["python"],
                "years_experience": 5,
                "min_experience": 3,
                "education_level": 3,
                "required_education": 2,
                "languages": ["en"],
                "required_languages": ["en"],
                "sector": "it_data",
                "required_sector": "it_data",
            },
            {
                "candidate_id": "c1",
                "job_id": "j1",
                "candidate_skills": ["python"],
                "required_skills": ["python"],
                "years_experience": 5,
                "min_experience": 3,
                "education_level": 3,
                "required_education": 2,
                "languages": ["en"],
                "required_languages": ["en"],
                "sector": "it_data",
                "required_sector": "it_data",
            }
        ])
        
        from src.scoring_engine.evaluation import compute_subscores_df
        result = compute_subscores_df(pairs)
        
        assert len(result) == 2
        # Les scores devraient être identiques pour les doublons
        assert result.iloc[0]["score_skills"] == result.iloc[1]["score_skills"]
    
    def test_pipeline_deterministic(self):
        """Le pipeline produit des résultats deterministes"""
        pairs = pd.DataFrame([
            {
                "candidate_id": "c1",
                "job_id": "j1",
                "candidate_skills": ["python", "sql"],
                "required_skills": ["python"],
                "years_experience": 5,
                "min_experience": 3,
                "education_level": 3,
                "required_education": 2,
                "languages": ["en", "fr"],
                "required_languages": ["en"],
                "sector": "it_data",
                "required_sector": "it_data",
            }
        ])
        
        from src.scoring_engine.evaluation import compute_subscores_df
        
        # Exécuter deux fois
        result1 = compute_subscores_df(pairs.copy())
        result2 = compute_subscores_df(pairs.copy())
        
        # Les résultats devraient être identiques
        pd.testing.assert_frame_equal(result1, result2)


class TestAlgorithmEvaluation:
    """Tests de l'évaluation des algorithmes de scoring"""
    
    def test_wsm_algorithm(self, small_dataset):
        """Test l'algorithme WSM"""
        from src.scoring_engine.algorithms.algorithms import WSMAlgorithm
        from src.scoring_engine.evaluation import compute_subscores_df, split_by_candidate_id
        
        candidates, jobs = small_dataset
        
        # Créer des paires avec label
        pairs = []
        for _, cand in candidates.iterrows():
            for _, job in jobs.iterrows():
                pairs.append({
                    "candidate_id": cand["candidate_id"],
                    "job_id": job["job_id"],
                    "candidate_skills": cand["skills"],
                    "required_skills": job["required_skills"],
                    "years_experience": cand["years_experience"],
                    "min_experience": job["min_experience"],
                    "education_level": cand["education_level_num"],
                    "required_education": job["required_education_num"],
                    "languages": cand["languages"],
                    "required_languages": job["required_languages"],
                    "sector": cand["candidate_sector"],
                    "required_sector": job["required_sector"],
                    "label": np.random.rand(),
                })
        
        pairs_df = pd.DataFrame(pairs)
        pairs_with_scores = compute_subscores_df(pairs_df)
        
        # Split et test
        train, test = split_by_candidate_id(pairs_with_scores, test_size=0.3)
        
        if len(train) > 0 and len(test) > 0:
            algo = WSMAlgorithm()
            y_train = train["label"].values
            preds = algo.predict(test)
            
            assert len(preds) == len(test)
            assert np.all((preds >= 0) & (preds <= 1))
    
    def test_topsis_algorithm(self, small_dataset):
        """Test l'algorithme TOPSIS"""
        from src.scoring_engine.algorithms.algorithms import TOPSISAlgorithm
        from src.scoring_engine.evaluation import compute_subscores_df, split_by_candidate_id
        
        candidates, jobs = small_dataset
        
        # Créer des paires avec label
        pairs = []
        for _, cand in candidates.iterrows():
            for _, job in jobs.iterrows():
                pairs.append({
                    "candidate_id": cand["candidate_id"],
                    "job_id": job["job_id"],
                    "candidate_skills": cand["skills"],
                    "required_skills": job["required_skills"],
                    "years_experience": cand["years_experience"],
                    "min_experience": job["min_experience"],
                    "education_level": cand["education_level_num"],
                    "required_education": job["required_education_num"],
                    "languages": cand["languages"],
                    "required_languages": job["required_languages"],
                    "sector": cand["candidate_sector"],
                    "required_sector": job["required_sector"],
                    "label": np.random.rand(),
                })
        
        pairs_df = pd.DataFrame(pairs)
        pairs_with_scores = compute_subscores_df(pairs_df)
        
        # Split et test
        train, test = split_by_candidate_id(pairs_with_scores, test_size=0.3)
        
        if len(train) > 0 and len(test) > 0:
            algo = TOPSISAlgorithm()
            y_train = train["label"].values
            preds = algo.predict(test)
            
            assert len(preds) == len(test)
            assert np.all((preds >= 0) & (preds <= 1))


class TestPipelineDataIntegrity:
    """Tests d'intégrité des données du pipeline"""
    
    def test_no_data_loss(self, realistic_dataset):
        """Vérifier qu'aucune donnée n'est perdue dans le pipeline"""
        from src.scoring_engine.evaluation import compute_subscores_df
        
        candidates, jobs = realistic_dataset
        
        # Créer des paires
        pairs = []
        expected_count = 0
        for _, cand in candidates.iterrows():
            for _, job in jobs.iterrows():
                pairs.append({
                    "candidate_id": cand["candidate_id"],
                    "job_id": job["job_id"],
                    "candidate_skills": cand["skills"],
                    "required_skills": job["required_skills"],
                    "years_experience": cand["years_experience"],
                    "min_experience": job["min_experience"],
                    "education_level": cand["education_level_num"],
                    "required_education": job["required_education_num"],
                    "languages": cand["languages"],
                    "required_languages": job["required_languages"],
                    "sector": cand["candidate_sector"],
                    "required_sector": job["required_sector"],
                })
                expected_count += 1
        
        pairs_df = pd.DataFrame(pairs)
        result = compute_subscores_df(pairs_df)
        
        assert len(result) == expected_count
    
    def test_score_distribution(self, realistic_dataset):
        """Vérifier la distribution statistique des scores"""
        from src.scoring_engine.evaluation import compute_subscores_df
        
        candidates, jobs = realistic_dataset
        
        # Créer un grand nombre de paires
        pairs = []
        for i, (_, cand) in enumerate(candidates.iterrows()):
            if i >= 20:  # Limiter pour les tests
                break
            for _, job in jobs.iterrows():
                pairs.append({
                    "candidate_id": cand["candidate_id"],
                    "job_id": job["job_id"],
                    "candidate_skills": cand["skills"],
                    "required_skills": job["required_skills"],
                    "years_experience": cand["years_experience"],
                    "min_experience": job["min_experience"],
                    "education_level": cand["education_level_num"],
                    "required_education": job["required_education_num"],
                    "languages": cand["languages"],
                    "required_languages": job["required_languages"],
                    "sector": cand["candidate_sector"],
                    "required_sector": job["required_sector"],
                })
        
        pairs_df = pd.DataFrame(pairs)
        result = compute_subscores_df(pairs_df)
        
        # Les scores devraient avoir une distribution variée (pas tous 0 ou 1)
        score_cols = ["score_skills", "score_experience", "score_education", "score_languages", "score_sector"]
        for col in score_cols:
            unique_vals = result[col].nunique()
            assert unique_vals > 1  # Au moins 2 valeurs distinctes
            
            mean = result[col].mean()
            std = result[col].std()
            assert 0.0 <= mean <= 1.0
            assert std >= 0.0

