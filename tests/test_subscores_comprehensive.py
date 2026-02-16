"""
test_subscores_comprehensive.py - Tests unitaires complets et détaillés de tous les subscores

Ce module teste:
- Chaque fonction de scoring indépendamment
- Cas normaux, cas limites, cas extrêmes
- Validations des valeurs d'entrée
- Cohérence des résultats
"""
import pytest
import pandas as pd
import numpy as np
from src.scoring_engine.components.subscores import (
    skills_jaccard,
    experience_score,
    education_score,
    languages_score,
    sector_score,
    compute_subscores,
)


class TestSkillsJaccard:
    """Tests pour la similarité Jaccard des compétences"""
    
    def test_identical_skills(self):
        """Deux candidats avec les mêmes compétences : score = 1.0"""
        assert skills_jaccard(["python", "sql"], ["python", "sql"]) == 1.0
    
    def test_no_common_skills(self):
        """Aucune compétence en commun : score = 0.0"""
        assert skills_jaccard(["python"], ["java"]) == 0.0
    
    def test_partial_overlap(self):
        """Compétences partiellement overlappantes"""
        result = skills_jaccard(["a", "b"], ["b", "c"])
        assert result == 1 / 3  # Intersection: {b}, Union: {a,b,c}
    
    def test_empty_candidate_skills(self):
        """Candidat sans compétences"""
        assert skills_jaccard([], ["python", "sql"]) == 0.0
        assert skills_jaccard(None, ["python"]) == 0.0
    
    def test_empty_job_skills(self):
        """Offre sans exigences de compétences"""
        assert skills_jaccard(["python"], []) == 0.0
        assert skills_jaccard(["python"], None) == 0.0
    
    def test_both_empty(self):
        """Ni candidat, ni offre sans compétences"""
        assert skills_jaccard([], []) == 0.0
    
    def test_subset_skills(self):
        """Compétences du candidat = sous-ensemble de celles requises"""
        result = skills_jaccard(["python"], ["python", "sql", "docker"])
        assert result == 1 / 3  # Intersection: {python}, Union: {python, sql, docker}
    
    def test_superset_skills(self):
        """Compétences du candidat = sur-ensemble de celles requises"""
        result = skills_jaccard(["python", "sql", "docker"], ["python"])
        assert result == 1 / 3  # Intersection: {python}, Union: {python, sql, docker}
    
    def test_case_insensitive(self):
        """Les compétences devraient être comparées correctement"""
        result = skills_jaccard(["Python", "SQL"], ["python", "sql"])
        # Conversion en string saféisé
        assert result > 0
    
    def test_result_in_valid_range(self):
        """Le résultat doit être entre 0 et 1"""
        for i in range(20):
            result = skills_jaccard(["a", "b"], ["b", "c", "d"])
            assert 0.0 <= result <= 1.0


class TestExperienceScore:
    """Tests pour le score d'expérience"""
    
    def test_exact_match(self):
        """Candidat avec expérience = minimum requis"""
        score = experience_score(5, 5)
        assert 0.8 <= score <= 1.0  # Devrait être haut
    
    def test_overqualified(self):
        """Candidat plus expérimenté que requis"""
        score = experience_score(10, 5)
        assert 0.7 <= score <= 1.0
    
    def test_underqualified(self):
        """Candidat moins expérimenté que requis"""
        score = experience_score(3, 5)
        assert 0.0 <= score < 0.8
    
    def test_no_experience_required(self):
        """Pas d'expérience requise"""
        score = experience_score(5, 0)
        assert 0.0 <= score <= 1.0
    
    def test_zero_experience_candidate(self):
        """Candidat sans expérience"""
        score = experience_score(0, 5)
        assert 0.0 <= score <= 1.0
    
    def test_senior_position(self):
        """Poste senior, candidat senior"""
        score = experience_score(15, 10)
        assert score > experience_score(3, 10)
    
    def test_junior_position(self):
        """Poste junio, candidat junior"""
        score = experience_score(2, 0)
        assert 0.0 <= score <= 1.0
    
    def test_none_values(self):
        """Gestion des valeurs None"""
        score1 = experience_score(None, 5)
        score2 = experience_score(5, None)
        assert 0.0 <= score1 <= 1.0
        assert 0.0 <= score2 <= 1.0
    
    def test_result_in_valid_range(self):
        """Vérifier que le résultat est toujours entre 0 et 1"""
        for cand_exp in [0, 1, 5, 10, 20]:
            for job_exp in [0, 2, 5, 10]:
                score = experience_score(cand_exp, job_exp)
                assert 0.0 <= score <= 1.0


class TestEducationScore:
    """Tests pour le score d'éducation"""
    
    def test_exact_level_match(self):
        """Candidat avec niveau = niveau requis"""
        score = education_score(4, 4)
        assert score == 1.0
    
    def test_higher_education(self):
        """Candidat plus diplômé que requis"""
        score = education_score(5, 3)
        assert score == 1.0
    
    def test_lower_education(self):
        """Candidat moins diplômé que requis"""
        score = education_score(2, 4)
        assert 0.0 <= score < 1.0
    
    def test_no_education_candidate(self):
        """Candidat sans éducation (niveau 0)"""
        score = education_score(0, 3)
        assert score == 0.0
    
    def test_no_education_required(self):
        """Pas de minimum requis"""
        score = education_score(3, 0)
        assert 0.0 <= score <= 1.0
    
    def test_both_zero(self):
        """Ni candidat, ni offre sans éducation"""
        score = education_score(0, 0)
        assert score == 0.0
    
    def test_progressive_scores(self):
        """Les scores doivent progresser avec le niveau"""
        score1 = education_score(1, 3)
        score2 = education_score(2, 3)
        score3 = education_score(3, 3)
        assert score1 < score2 < score3
    
    def test_none_values(self):
        """Gestion des valeurs None"""
        score1 = education_score(None, 3)
        score2 = education_score(3, None)
        assert 0.0 <= score1 <= 1.0
        assert 0.0 <= score2 <= 1.0
    
    def test_result_in_valid_range(self):
        """Vérifier que le résultat est toujours entre 0 et 1"""
        for cand_edu in [0, 1, 2, 3, 4, 5]:
            for job_edu in [0, 1, 2, 3, 4, 5]:
                score = education_score(cand_edu, job_edu)
                assert 0.0 <= score <= 1.0


class TestLanguagesScore:
    """Tests pour le score de langues"""
    
    def test_identical_languages(self):
        """Candidat avec les mêmes langues que requises"""
        score = languages_score(["en", "fr"], ["en", "fr"])
        assert score == 1.0
    
    def test_subset_of_required(self):
        """Candidat parle un sous-ensemble des langues requises"""
        score = languages_score(["en"], ["en", "fr"])
        assert score == 0.5  # 1 sur 2 langues requises
    
    def test_more_languages_than_required(self):
        """Candidat parle plus de langues que requis"""
        score = languages_score(["en", "fr", "de"], ["en"])
        assert score == 1.0  # Toutes les langues requises couvertes
    
    def test_no_common_language(self):
        """Candidat without required languages"""
        score = languages_score(["de", "it"], ["en", "fr"])
        assert score == 0.0
    
    def test_no_languages_required(self):
        """Pas de langues requises"""
        score = languages_score(["en"], [])
        assert score == 1.0
    
    def test_candidate_no_languages(self):
        """Candidat sans langues"""
        score = languages_score([], ["en"])
        assert score == 0.0
    
    def test_both_no_languages(self):
        """Ni candidat, ni offre sans langues"""
        score = languages_score([], [])
        assert score == 1.0
    
    def test_none_values(self):
        """Gestion des valeurs None"""
        score1 = languages_score(None, ["en"])
        score2 = languages_score(["en"], None)
        assert 0.0 <= score1 <= 1.0
        assert 0.0 <= score2 <= 1.0
    
    def test_result_in_valid_range(self):
        """Vérifier que le résultat est toujours entre 0 et 1"""
        for cand_langs in [[], ["en"], ["en", "fr"]]:
            for job_langs in [[], ["en"], ["en", "fr"]]:
                score = languages_score(cand_langs, job_langs)
                assert 0.0 <= score <= 1.0


class TestSectorScore:
    """Tests pour le score de secteur"""
    
    def test_same_sector(self):
        """Candidat et poste dans le même secteur"""
        score = sector_score("it_data", "it_data")
        assert score == 1.0
    
    def test_different_sector(self):
        """Candidat et poste dans des secteurs différents"""
        score = sector_score("it_data", "finance")
        assert score == 0.5  # Pénalité mais pas 0
    
    def test_none_candidate_sector(self):
        """Candidat sans secteur spécifié"""
        score = sector_score(None, "it_data")
        assert score == 0.0
    
    def test_none_job_sector(self):
        """Offre sans secteur spécifié"""
        score = sector_score("it_data", None)
        assert score == 0.0
    
    def test_both_none_sector(self):
        """Ni candidat, ni offre sans secteur"""
        score = sector_score(None, None)
        assert score == 0.0
    
    def test_empty_string_sector(self):
        """Secteur = chaîne vide"""
        score1 = sector_score("", "it_data")
        score2 = sector_score("it_data", "")
        assert score1 == 0.0
        assert score2 == 0.0
    
    def test_case_sensitivity(self):
        """Les secteurs sont sensibles à la casse"""
        score1 = sector_score("IT_DATA", "it_data")
        score2 = sector_score("it_data", "it_data")
        # Dépend de l'implémentation
        assert 0.0 <= score1 <= 1.0
        assert score2 == 1.0
    
    def test_result_in_valid_range(self):
        """Vérifier que le résultat est 0, 0.5 ou 1"""
        for cs in ["it_data", "finance", None]:
            for js in ["it_data", "finance", None]:
                score = sector_score(cs, js)
                assert score in [0.0, 0.5, 1.0]


class TestComputeSubscores:
    """Tests pour la fonction globale compute_subscores"""
    
    def test_basic_dataframe(self, realistic_dataset):
        """Calcul les subscores sur un dataframe basique"""
        candidates, jobs = realistic_dataset
        # Créer une paire simple
        pairs = pd.DataFrame([{
            "candidate_id": candidates.iloc[0]["candidate_id"],
            "job_id": jobs.iloc[0]["job_id"],
            "candidate_skills": candidates.iloc[0]["skills"],
            "required_skills": jobs.iloc[0]["required_skills"],
            "years_experience": candidates.iloc[0]["years_experience"],
            "min_experience": jobs.iloc[0]["min_experience"],
            "education_level": candidates.iloc[0]["education_level_num"],
            "required_education": jobs.iloc[0]["required_education_num"],
            "languages": candidates.iloc[0]["languages"],
            "required_languages": jobs.iloc[0]["required_languages"],
            "sector": candidates.iloc[0]["candidate_sector"],
            "required_sector": jobs.iloc[0]["required_sector"],
        }])
        
        result = compute_subscores(pairs)
        
        # Vérifier que les colonnes de score sont créées
        assert "score_skills" in result.columns
        assert "score_experience" in result.columns
        assert "score_education" in result.columns
        assert "score_languages" in result.columns
        assert "score_sector" in result.columns
    
    def test_subscores_in_valid_range(self, realistic_dataset):
        """Tous les subscores doivent être entre 0 et 1"""
        candidates, jobs = realistic_dataset
        
        # Créer plusieurs paires
        pairs = []
        for i in range(min(5, len(candidates))):
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
        result = compute_subscores(pairs_df)
        
        score_cols = ["score_skills", "score_experience", "score_education", "score_languages", "score_sector"]
        for col in score_cols:
            assert (result[col] >= 0.0).all() and (result[col] <= 1.0).all()
    
    def test_edge_cases(self, edge_case_dataset):
        """Tester les cas limites"""
        candidates, jobs = edge_case_dataset
        
        # Créer des paires avec cas limites
        pairs = []
        for i in range(len(candidates)):
            for j in range(len(jobs)):
                pairs.append({
                    "candidate_id": candidates.iloc[i]["candidate_id"],
                    "job_id": jobs.iloc[j]["job_id"],
                    "candidate_skills": candidates.iloc[i]["skills"],
                    "required_skills": jobs.iloc[j]["required_skills"],
                    "years_experience": candidates.iloc[i]["years_experience"],
                    "min_experience": jobs.iloc[j]["min_experience"],
                    "education_level": candidates.iloc[i]["education_level_num"],
                    "required_education": jobs.iloc[j]["required_education_num"],
                    "languages": candidates.iloc[i]["languages"],
                    "required_languages": jobs.iloc[j]["required_languages"],
                    "sector": candidates.iloc[i]["candidate_sector"],
                    "required_sector": jobs.iloc[j]["required_sector"],
                })
        
        pairs_df = pd.DataFrame(pairs)
        result = compute_subscores(pairs_df)
        
        # Vérifier la cohérence
        assert len(result) == len(pairs_df)
        assert not result.isnull().any().any()  # Pas de NaN
    
    def test_large_batch(self, large_dataset):
        """Tester avec un grand dataset"""
        candidates, jobs = large_dataset
        
        # Créer un sample de paires
        pairs = []
        for i in range(min(100, len(candidates))):
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
        result = compute_subscores(pairs_df)
        
        assert len(result) == len(pairs_df)
        assert not result.isnull().any().any()


class TestSubscoresConsistency:
    """Tests de cohérence inter-subscores"""
    
    def test_perfect_match_high_scores(self):
        """Un candidat parfait = scores élevés sur tous les critères"""
        pairs = pd.DataFrame([{
            "candidate_skills": ["python", "sql"],
            "required_skills": ["python", "sql"],
            "years_experience": 10,
            "min_experience": 5,
            "education_level": 4,
            "required_education": 3,
            "languages": ["en", "fr"],
            "required_languages": ["en"],
            "sector": "it_data",
            "required_sector": "it_data",
        }])
        
        result = compute_subscores(pairs)
        
        # Tous les scores devraient être élevés
        assert result.iloc[0]["score_skills"] >= 0.8
        assert result.iloc[0]["score_experience"] >= 0.8
        assert result.iloc[0]["score_education"] >= 0.8
        assert result.iloc[0]["score_languages"] >= 0.8
        assert result.iloc[0]["score_sector"] >= 0.8
    
    def test_poor_match_low_scores(self):
        """Un candidat mal assorti = scores bas sur la plupart"""
        pairs = pd.DataFrame([{
            "candidate_skills": ["fortran"],
            "required_skills": ["python", "sql"],
            "years_experience": 0,
            "min_experience": 10,
            "education_level": 1,
            "required_education": 5,
            "languages": ["de"],
            "required_languages": ["en", "fr"],
            "sector": "healthcare",
            "required_sector": "it_data",
        }])
        
        result = compute_subscores(pairs)
        
        # Scores devraient être faibles
        assert result.iloc[0]["score_skills"] <= 0.1
        assert result.iloc[0]["score_experience"] <= 0.2
        assert result.iloc[0]["score_sector"] <= 0.5
    
    def test_monotonicity(self):
        """Si un attribut s'améliore, le score ne devrait pas diminuer"""
        base_pairs = pd.DataFrame([{
            "candidate_skills": ["python"],
            "required_skills": ["python"],
            "years_experience": 2,
            "min_experience": 5,
            "education_level": 2,
            "required_education": 3,
            "languages": ["en"],
            "required_languages": ["en"],
            "sector": "it_data",
            "required_sector": "it_data",
        }])
        
        improved_pairs = pd.DataFrame([{
            "candidate_skills": ["python", "sql"],
            "required_skills": ["python"],
            "years_experience": 5,  # Amélioration
            "min_experience": 5,
            "education_level": 2,
            "required_education": 3,
            "languages": ["en"],
            "required_languages": ["en"],
            "sector": "it_data",
            "required_sector": "it_data",
        }])
        
        base_result = compute_subscores(base_pairs)
        improved_result = compute_subscores(improved_pairs)
        
        # Le score d'expérience devrait augmenter
        assert improved_result.iloc[0]["score_experience"] >= base_result.iloc[0]["score_experience"]
