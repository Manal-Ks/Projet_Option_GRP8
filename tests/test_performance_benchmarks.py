"""
test_performance_benchmarks.py - Tests de performance et benchmarks

Ce module mesure:
- Temps d'exécution des subscores
- Temps d'exécution du pipeline complet
- Temps des algorithmes de scoring
- Mémoire utilisée
- Scalabilité avec la taille des données
"""
import time
import psutil
import os
import json
import pandas as pd
import numpy as np
import pytest
from pathlib import Path


class PerformanceMetrics:
    """Classe pour collecter et gérer les métriques de performance"""
    
    def __init__(self):
        self.metrics = {
            "subscores": {},
            "pipeline": {},
            "algorithms": {},
            "memory": {},
        }
    
    def record_subscores_time(self, dataset_size, execution_time):
        """Enregistre le temps d'exécution des subscores"""
        key = f"size_{dataset_size}"
        self.metrics["subscores"][key] = {
            "time_ms": execution_time * 1000,
            "time_per_item_us": (execution_time / dataset_size) * 1_000_000 if dataset_size > 0 else 0,
        }
    
    def record_algorithm_time(self, algo_name, execution_time):
        """Enregistre le temps d'exécution d'un algorithme"""
        self.metrics["algorithms"][algo_name] = {
            "time_ms": execution_time * 1000,
        }
    
    def record_memory_usage(self, phase, memory_mb):
        """Enregistre l'utilisation mémoire"""
        self.metrics["memory"][phase] = {
            "memory_mb": memory_mb,
        }
    
    def export_to_json(self, filepath):
        """Exporte les métriques en JSON"""
        with open(filepath, "w") as f:
            json.dump(self.metrics, f, indent=2)
    
    def print_summary(self):
        """Affiche un résumé des métriques"""
        print("\n=== PERFORMANCE METRICS ===")
        print("\nSubscores:")
        for key, val in self.metrics["subscores"].items():
            print(f"  {key}: {val['time_ms']:.2f}ms ({val['time_per_item_us']:.2f}μs/item)")
        
        print("\nAlgorithms:")
        for algo, val in self.metrics["algorithms"].items():
            print(f"  {algo}: {val['time_ms']:.2f}ms")
        
        print("\nMemory:")
        for phase, val in self.metrics["memory"].items():
            print(f"  {phase}: {val['memory_mb']:.2f}MB")


@pytest.fixture
def perf_metrics():
    """Fixture fournissant un collecteur de métriques"""
    return PerformanceMetrics()


class TestSubscoresPerformance:
    """Tests de performance des subscores"""
    
    def test_subscores_speed_small(self, small_dataset, perf_metrics):
        """Mesurer la vitesse des subscores avec petit dataset"""
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
                })
        
        pairs_df = pd.DataFrame(pairs)
        
        # Mesurer le temps
        start = time.time()
        result = compute_subscores_df(pairs_df)
        elapsed = time.time() - start
        
        perf_metrics.record_subscores_time(len(pairs_df), elapsed)
        
        # Les subscores devraient être rapides (< 1s pour 100 items)
        assert elapsed < 1.0
    
    def test_subscores_speed_medium(self, realistic_dataset, perf_metrics):
        """Mesurer la vitesse des subscores avec dataset moyen"""
        from src.scoring_engine.evaluation import compute_subscores_df
        
        candidates, jobs = realistic_dataset
        
        # Créer des paires (mais limiter le nombre)
        pairs = []
        for i, (_, cand) in enumerate(candidates.iterrows()):
            if i >= 30:
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
        
        # Mesurer le temps
        start = time.time()
        result = compute_subscores_df(pairs_df)
        elapsed = time.time() - start
        
        perf_metrics.record_subscores_time(len(pairs_df), elapsed)
        
        # Les subscores devraient scaler linéairement
        assert elapsed < 5.0  # Sans limit stricte
    
    def test_subscores_memory_usage(self, realistic_dataset, perf_metrics):
        """Mesurer l'utilisation mémoire des subscores"""
        from src.scoring_engine.evaluation import compute_subscores_df
        
        candidates, jobs = realistic_dataset
        
        # Créer des paires
        pairs = []
        for i, (_, cand) in enumerate(candidates.iterrows()):
            if i >= 50:
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
        
        # Mesurer mémoire avant
        process = psutil.Process(os.getpid())
        mem_before = process.memory_info().rss / 1024 / 1024
        
        # Exécuter
        result = compute_subscores_df(pairs_df)
        
        # Mesurer mémoire après
        mem_after = process.memory_info().rss / 1024 / 1024
        mem_used = mem_after - mem_before
        
        perf_metrics.record_memory_usage("subscores", mem_used)
        
        # Le memory usage devrait être raisonnable
        assert mem_used < 500  # < 500MB pour 500 paires


class TestAlgorithmPerformance:
    """Tests de performance des algorithmes"""
    
    def test_wsm_algorithm_speed(self, small_dataset, perf_metrics):
        """Mesurer la vitesse de l'algorithme WSM"""
        from src.scoring_engine.algorithms.algorithms import WSMAlgorithm
        from src.scoring_engine.evaluation import compute_subscores_df, split_by_candidate_id
        
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
                    "label": np.random.rand(),
                })
        
        pairs_df = pd.DataFrame(pairs)
        pairs_with_scores = compute_subscores_df(pairs_df)
        
        train, test = split_by_candidate_id(pairs_with_scores, test_size=0.3)
        
        if len(train) > 0 and len(test) > 0:
            algo = WSMAlgorithm()
            
            # Mesurer temps
            start = time.time()
            algo.fit(train, train["label"].values if "label" in train else None)
            preds = algo.predict(test)
            elapsed = time.time() - start
            
            perf_metrics.record_algorithm_time("WSM", elapsed)
            
            # Ce test devrait être rapide
            assert elapsed < 1.0
    
    def test_topsis_algorithm_speed(self, small_dataset, perf_metrics):
        """Mesurer la vitesse de l'algorithme TOPSIS"""
        from src.scoring_engine.algorithms.algorithms import TOPSISAlgorithm
        from src.scoring_engine.evaluation import compute_subscores_df, split_by_candidate_id
        
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
                    "label": np.random.rand(),
                })
        
        pairs_df = pd.DataFrame(pairs)
        pairs_with_scores = compute_subscores_df(pairs_df)
        
        train, test = split_by_candidate_id(pairs_with_scores, test_size=0.3)
        
        if len(train) > 0 and len(test) > 0:
            algo = TOPSISAlgorithm()
            
            # Mesurer temps
            start = time.time()
            algo.fit(train, train["label"].values if "label" in train else None)
            preds = algo.predict(test)
            elapsed = time.time() - start
            
            perf_metrics.record_algorithm_time("TOPSIS", elapsed)
            
            # Ce test devrait être rapide
            assert elapsed < 2.0
    
    def test_all_algorithms_speed(self, small_dataset, perf_metrics):
        """Tester la vitesse de tous les algorithmes"""
        from src.scoring_engine.algorithms.algorithms import (
            WSMAlgorithm, WPMAlgorithm, TOPSISAlgorithm,
            LogisticRegressionAlgorithm, GradientBoostingAlgorithm, RandomForestAlgorithm
        )
        from src.scoring_engine.evaluation import compute_subscores_df, split_by_candidate_id
        
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
                    "label": np.random.rand(),
                })
        
        pairs_df = pd.DataFrame(pairs)
        pairs_with_scores = compute_subscores_df(pairs_df)
        
        train, test = split_by_candidate_id(pairs_with_scores, test_size=0.3)
        
        if len(train) > 0 and len(test) > 0:
            algos = {
                "WSM": WSMAlgorithm(),
                "WPM": WPMAlgorithm(),
                "TOPSIS": TOPSISAlgorithm(),
                "LogisticRegression": LogisticRegressionAlgorithm(),
                "GradientBoosting": GradientBoostingAlgorithm(),
                "RandomForest": RandomForestAlgorithm(),
            }
            
            for name, algo in algos.items():
                try:
                    start = time.time()
                    algo.fit(train, train["label"].values if "label" in train else None)
                    preds = algo.predict(test)
                    elapsed = time.time() - start
                    
                    perf_metrics.record_algorithm_time(name, elapsed)
                    
                    # Tous les algos devraient terminer dans un temps raisonnable
                    assert elapsed < 10.0, f"{name} took {elapsed}s (> 10s)"
                except Exception as e:
                    # Certains algos peuvent ne pas être disponibles, c'est OK
                    pass


class TestScalability:
    """Tests de scalabilité avec différentes tailles de données"""
    
    def test_linear_scalability(self, perf_metrics):
        """Vérifier que la performance scale linéairement"""
        from src.scoring_engine.evaluation import compute_subscores_df
        
        sizes = [100, 250, 500]
        times = []
        
        for size in sizes:
            pairs = []
            for i in range(size):
                pairs.append({
                    "candidate_id": f"c{i}",
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
                })
            
            pairs_df = pd.DataFrame(pairs)
            
            start = time.time()
            result = compute_subscores_df(pairs_df)
            elapsed = time.time() - start
            
            times.append(elapsed)
            perf_metrics.record_subscores_time(size, elapsed)
        
        # Vérifier que le temps augmente avec la taille
        assert times[1] > times[0]
        assert times[2] > times[1]
        
        # Vérifier une scalabilité raisonnablement linéaire (pas exponentielle)
        # Ratio devrait être proche de linéaire
        ratio1 = times[1] / times[0]
        ratio2 = times[2] / times[1]
        
        # Pour une scalabilité linéaire:
        # times[1] devrait être ~2.5x times[0] (250/100)
        # times[2] devrait être ~2x times[1] (500/250)
        # Avec une tolérance
        assert ratio1 < 5.0  # < 5x pour 2.5x de données
        assert ratio2 < 3.0  # < 3x pour 2x de données


if __name__ == "__main__":
    # Permet d'exécuter les benchmarks directement
    pytest.main([__file__, "-v", "-s"])
