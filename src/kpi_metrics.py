"""
kpi_metrics.py - Métriques KPI pour évaluer la stabilité et robustesse du système

Ce module calcule:
- KPI de stabilité (consistency d'exécution)
- KPI de robustesse (handling erreurs et edge cases)
- KPI de performance (speed, memory)
- KPI de qualité (accuracy, ranking quality)
"""
import numpy as np
import pandas as pd
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


@dataclass
class KPIMetrics:
    """Structure pour ranger les KPIs"""
    
    # Stabilité
    stability_score: float  # 0-1
    consistency_rate: float  # % de consistency
    variance_coefficient: float  # Variation des scores
    
    # Robustesse
    robustness_score: float  # 0-1
    error_rate: float  # % d'erreurs
    edge_case_handling: float  # % de cas limites gérés correctement
    
    # Performance
    avg_latency_ms: float  # Temps moyen d'exécution
    memory_usage_mb: float  # Mémoire utilisée
    throughput_per_second: float  # Paires par seconde
    
    # Qualité
    data_quality_score: float  # 0-1
    score_distribution_health: float  # 0-1
    correlation_health: float  # 0-1
    
    # Score global
    overall_health_score: float  # 0-1
    
    @property
    def summary(self) -> Dict[str, float]:
        """Résumé des KPIs principaux"""
        return {
            "Stability": self.stability_score,
            "Robustness": self.robustness_score,
            "Performance": 1.0 - (self.avg_latency_ms / 1000),  # 1.0 pour < 1ms
            "Quality": self.data_quality_score,
            "Overall": self.overall_health_score,
        }


class KPICalculator:
    """Calcule les KPIs du système"""
    
    # Seuils d'alerte
    STABILITY_WARN_THRESHOLD = 0.90
    ROBUSTNESS_WARN_THRESHOLD = 0.95
    PERFORMANCE_WARN_LATENCY_MS = 100
    QUALITY_WARN_THRESHOLD = 0.85
    
    @staticmethod
    def calculate_all(
        execution_records: List[Dict],
        score_df: pd.DataFrame,
        performance_data: Dict,
    ) -> KPIMetrics:
        """Calcule tous les KPIs"""
        
        # Stabilité
        stability_score = KPICalculator._calculate_stability(execution_records)
        
        # Robustesse
        robustness_score = KPICalculator._calculate_robustness(execution_records)
        
        # Performance
        avg_latency, memory_usage, throughput = KPICalculator._calculate_performance(performance_data)
        
        # Qualité
        data_quality, score_health, corr_health = KPICalculator._calculate_quality(score_df)
        
        # Score global
        overall_health = KPICalculator._calculate_overall_health(
            stability_score, robustness_score, data_quality
        )
        
        return KPIMetrics(
            stability_score=stability_score,
            consistency_rate=stability_score * 100,
            variance_coefficient=1.0 - KPICalculator._calculate_variance_coefficient(score_df),
            robustness_score=robustness_score,
            error_rate=(1.0 - robustness_score) * 100,
            edge_case_handling=robustness_score * 100,
            avg_latency_ms=avg_latency,
            memory_usage_mb=memory_usage,
            throughput_per_second=throughput,
            data_quality_score=data_quality,
            score_distribution_health=score_health,
            correlation_health=corr_health,
            overall_health_score=overall_health,
        )
    
    @staticmethod
    def _calculate_stability(execution_records: List[Dict]) -> float:
        """KPI : Stabilité (% d'exécutions réussies et cohérentes)"""
        
        if not execution_records:
            return 0.0
        
        successful = sum(1 for r in execution_records if r.get("status") == "success")
        stability = successful / len(execution_records)
        
        # Pénalité pour variance élevée
        if len(execution_records) > 1:
            latencies = [r.get("latency_ms", 0) for r in execution_records]
            variance = np.std(latencies) / (np.mean(latencies) + 1e-6)
            stability *= max(0, 1 - variance * 0.1)
        
        return float(np.clip(stability, 0.0, 1.0))
    
    @staticmethod
    def _calculate_robustness(execution_records: List[Dict]) -> float:
        """KPI : Robustesse (% de cas limites gérés correctement)"""
        
        if not execution_records:
            return 0.0
        
        # Total d'exécutions
        total = len(execution_records)
        
        # Exécutions menant à erreur
        errors = sum(1 for r in execution_records if r.get("error") is not None)
        error_rate = errors / total
        
        # Cas limites gérés
        edge_cases = sum(1 for r in execution_records if r.get("is_edge_case", False))
        edge_cases_handled = sum(1 for r in execution_records 
                                if r.get("is_edge_case", False) and r.get("status") == "success")
        edge_case_rate = edge_cases_handled / edge_cases if edge_cases > 0 else 1.0
        
        # Score de robustesse = (1 - error_rate) * edge_case_rate
        robustness = (1.0 - error_rate * 0.5) * edge_case_rate
        
        return float(np.clip(robustness, 0.0, 1.0))
    
    @staticmethod
    def _calculate_performance(performance_data: Dict) -> Tuple[float, float, float]:
        """KPI : Performance (latence, mémoire, throughput)"""
        
        avg_latency = performance_data.get("avg_latency_ms", 0)
        memory_usage = performance_data.get("memory_usage_mb", 0)
        throughput = performance_data.get("throughput_per_second", 1)
        
        return float(avg_latency), float(memory_usage), float(throughput)
    
    @staticmethod
    def _calculate_quality(score_df: pd.DataFrame) -> Tuple[float, float, float]:
        """KPI : Qualité (distribution, santé des données)"""
        
        score_cols = ["score_skills", "score_experience", "score_education", 
                     "score_languages", "score_sector"]
        
        # 1) Intégrité des données
        data_quality = 1.0
        for col in score_cols:
            if col not in score_df.columns:
                data_quality -= 0.2
            else:
                null_rate = score_df[col].isnull().sum() / len(score_df)
                if null_rate > 0:
                    data_quality -= null_rate * 0.1
                
                # Vérifier la plage [0, 1]
                out_of_range = ((score_df[col] < 0) | (score_df[col] > 1)).sum() / len(score_df)
                if out_of_range > 0:
                    data_quality -= out_of_range * 0.2
        
        data_quality = float(np.clip(data_quality, 0.0, 1.0))
        
        # 2) Santé de la distribution (pas tous 0 ou 1)
        score_health = 1.0
        for col in score_cols:
            if col in score_df.columns:
                std = score_df[col].std()
                # Pénalité si std est trop bas (tous identiques)
                if std < 0.01:
                    score_health -= 0.15
                # Pénalité si la distribution est trop concentrée aux extrêmes
                mean = score_df[col].mean()
                if (mean < 0.1 or mean > 0.9) and std < 0.2:
                    score_health -= 0.1
        
        score_health = float(np.clip(score_health, 0.0, 1.0))
        
        # 3) Santé des corrélations (pas d'extrêmes)
        corr_health = KPICalculator._calculate_correlation_health(score_df, score_cols)
        
        return data_quality, score_health, corr_health
    
    @staticmethod
    def _calculate_correlation_health(df: pd.DataFrame, score_cols: List[str]) -> float:
        """Évalue la santé des corrélations (pas d'extrêmes)"""
        
        health = 1.0
        num_corrs = 0
        
        for i, col1 in enumerate(score_cols):
            if col1 not in df.columns:
                continue
            
            for col2 in score_cols[i+1:]:
                if col2 not in df.columns:
                    continue
                
                try:
                    corr = df[col1].corr(df[col2])
                    if abs(corr) > 0.85:  # Corrélation extrême
                        health -= 0.1
                    num_corrs += 1
                except:
                    pass
        
        return float(np.clip(health, 0.0, 1.0))
    
    @staticmethod
    def _calculate_variance_coefficient(score_df: pd.DataFrame) -> float:
        """Calcule le coefficient de variation (spread des données)"""
        
        score_cols = ["score_skills", "score_experience", "score_education", 
                     "score_languages", "score_sector"]
        
        coefficients = []
        for col in score_cols:
            if col in score_df.columns:
                mean = score_df[col].mean()
                std = score_df[col].std()
                if mean > 0:
                    coef = std / mean
                    coefficients.append(max(0, min(1, coef)))
        
        return float(np.mean(coefficients)) if coefficients else 0.0
    
    @staticmethod
    def _calculate_overall_health(stability: float, robustness: float, quality: float) -> float:
        """Calcule le score de santé global (average pondéré)"""
        
        # Pondération: Qualité > Stabilité > Robustesse
        overall = (quality * 0.4) + (stability * 0.4) + (robustness * 0.2)
        
        return float(np.clip(overall, 0.0, 1.0))


# Thresholds et alertes
class KPIThresholds:
    """Helper pour interpréter les KPIs"""
    
    STATUS_CRITICAL = "🔴 CRITICAL"
    STATUS_WARNING = "🟡 WARNING"
    STATUS_OK = "🟢 OK"
    STATUS_EXCELLENT = "✅ EXCELLENT"
    
    @staticmethod
    def get_stability_status(score: float) -> str:
        """Retourne le status basé sur le score de stabilité"""
        if score < 0.80:
            return KPIThresholds.STATUS_CRITICAL
        elif score < 0.90:
            return KPIThresholds.STATUS_WARNING
        elif score < 0.97:
            return KPIThresholds.STATUS_OK
        else:
            return KPIThresholds.STATUS_EXCELLENT
    
    @staticmethod
    def get_robustness_status(score: float) -> str:
        """Retourne le status basé sur le score de robustesse"""
        if score < 0.85:
            return KPIThresholds.STATUS_CRITICAL
        elif score < 0.93:
            return KPIThresholds.STATUS_WARNING
        elif score < 0.98:
            return KPIThresholds.STATUS_OK
        else:
            return KPIThresholds.STATUS_EXCELLENT
    
    @staticmethod
    def get_quality_status(score: float) -> str:
        """Retourne le status basé sur le score de qualité"""
        if score < 0.80:
            return KPIThresholds.STATUS_CRITICAL
        elif score < 0.88:
            return KPIThresholds.STATUS_WARNING
        elif score < 0.95:
            return KPIThresholds.STATUS_OK
        else:
            return KPIThresholds.STATUS_EXCELLENT
    
    @staticmethod
    def get_performance_status(latency_ms: float) -> str:
        """Retourne le status basé sur la latence"""
        if latency_ms > 1000:
            return KPIThresholds.STATUS_CRITICAL
        elif latency_ms > 500:
            return KPIThresholds.STATUS_WARNING
        elif latency_ms > 100:
            return KPIThresholds.STATUS_OK
        else:
            return KPIThresholds.STATUS_EXCELLENT


def print_kpi_report(metrics: KPIMetrics):
    """Affiche un rapport KPI formaté"""
    
    print("\n" + "="*70)
    print("KPI METRICS REPORT")
    print("="*70)
    
    print(f"\nSTABILITY & CONSISTENCY:")
    print(f"  Stability Score: {metrics.stability_score:.2%} {KPIThresholds.get_stability_status(metrics.stability_score)}")
    print(f"  Consistency Rate: {metrics.consistency_rate:.1f}%")
    print(f"  Variance Coeff: {metrics.variance_coefficient:.3f}")
    
    print(f"\nROBUSTNESS:")
    print(f"  Robustness Score: {metrics.robustness_score:.2%} {KPIThresholds.get_robustness_status(metrics.robustness_score)}")
    print(f"  Error Rate: {metrics.error_rate:.2f}%")
    print(f"  Edge Case Handling: {metrics.edge_case_handling:.1f}%")
    
    print(f"\nPERFORMANCE:")
    print(f"  Avg Latency: {metrics.avg_latency_ms:.2f}ms {KPIThresholds.get_performance_status(metrics.avg_latency_ms)}")
    print(f"  Memory Usage: {metrics.memory_usage_mb:.2f}MB")
    print(f"  Throughput: {metrics.throughput_per_second:.0f} pairs/sec")
    
    print(f"\nDATA QUALITY:")
    print(f"  Data Quality: {metrics.data_quality_score:.2%} {KPIThresholds.get_quality_status(metrics.data_quality_score)}")
    print(f"  Score Distribution Health: {metrics.score_distribution_health:.2%}")
    print(f"  Correlation Health: {metrics.correlation_health:.2%}")
    
    print(f"\nOVERALL HEALTH SCORE: {metrics.overall_health_score:.2%}")
    
    print("\n" + "="*70)
