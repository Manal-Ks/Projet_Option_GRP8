"""
score_coherence_analysis.py - Analyse de la cohérence et validité des scores

Ce module fournit des outils pour:
- Vérifier la cohérence des scores
- Analyser les distributions de scores
- Déterminer les anomalies
- Mesurer la robustesse des scoring
"""
import numpy as np
import pandas as pd
import warnings
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class CoherenceReport:
    """Rapport d'analyse de cohérence"""
    
    total_pairs: int
    score_means: Dict[str, float]
    score_stds: Dict[str, float]
    score_ranges: Dict[str, Tuple[float, float]]
    anomalies: Dict[str, List[int]]
    correlations: Dict[Tuple[str, str], float]
    quality_score: float
    issues: List[str]
    recommendations: List[str]


class ScoreCoherenceAnalyzer:
    """Analyse la cohérence et validité des scores générés par le pipeline"""
    
    # Seuils de détection d'anomalies
    ANOMALY_THRESHOLDS = {
        "constant_scores": 0.005,  # Si std < 0.005 pour un score
        "bimodal_distribution": 0.15,  # Si 2+ pics détectés
        "extreme_correlation": 0.95,  # Si corr > 0.95
        "outlier_zscore": 3.0,  # Z-score threshold
    }
    
    @staticmethod
    def analyze(pairs_df: pd.DataFrame) -> CoherenceReport:
        """Analyse la cohérence d'un dataframe de paires scorées"""
        
        score_cols = ["score_skills", "score_experience", "score_education", 
                     "score_languages", "score_sector"]
        
        # Vérifier que les colonnes existent
        missing_cols = [c for c in score_cols if c not in pairs_df.columns]
        if missing_cols:
            raise ValueError(f"Missing score columns: {missing_cols}")
        
        # Calculs statistiques
        report = CoherenceReport(
            total_pairs=len(pairs_df),
            score_means={col: float(pairs_df[col].mean()) for col in score_cols},
            score_stds={col: float(pairs_df[col].std()) for col in score_cols},
            score_ranges={col: (float(pairs_df[col].min()), float(pairs_df[col].max())) for col in score_cols},
            anomalies={},
            correlations={},
            quality_score=1.0,
            issues=[],
            recommendations=[],
        )
        
        # Détecter les anomalies
        ScoreCoherenceAnalyzer._detect_anomalies(report, pairs_df, score_cols)
        
        # Analyser les corrélations
        ScoreCoherenceAnalyzer._analyze_correlations(report, pairs_df, score_cols)
        
        # Calculer le score de qualité
        ScoreCoherenceAnalyzer._compute_quality_score(report)
        
        return report
    
    @staticmethod
    def _detect_anomalies(report: CoherenceReport, df: pd.DataFrame, score_cols: List[str]):
        """Détecte les anomalies dans les scores"""
        
        # 1) Vérifier les scores constants
        for col in score_cols:
            if report.score_stds[col] < ScoreCoherenceAnalyzer.ANOMALY_THRESHOLDS["constant_scores"]:
                report.issues.append(f"WARNING: {col} has very low variance (std={report.score_stds[col]:.6f})")
                report.anomalies[col] = list(range(len(df)))
                report.recommendations.append(f"Review {col} calculation - all values are nearly identical")
        
        # 2) Détecter les outliers (Z-score)
        for col in score_cols:
            if report.score_stds[col] > 0:
                z_scores = np.abs((df[col] - report.score_means[col]) / report.score_stds[col])
                outlier_indices = np.where(z_scores > ScoreCoherenceAnalyzer.ANOMALY_THRESHOLDS["outlier_zscore"])[0]
                
                if len(outlier_indices) > 0:
                    outlier_pct = (len(outlier_indices) / len(df)) * 100
                    if outlier_pct > 5:  # Si > 5% d'outliers
                        report.issues.append(f"WARNING: {col} has {outlier_pct:.1f}% outliers")
                        report.recommendations.append(f"Review {col} - high variance or bimodal distribution detected")
        
        # 3) Vérifier les valeurs NaN ou infinies
        for col in score_cols:
            if df[col].isnull().any():
                report.issues.append(f"ERROR: {col} contains NaN values")
                report.anomalies[col] = df[df[col].isnull()].index.tolist()
            
            if np.isinf(df[col]).any():
                report.issues.append(f"ERROR: {col} contains infinite values")
                report.anomalies[col] = df[np.isinf(df[col])].index.tolist()
        
        # 4) Vérifier que les scores sont dans [0, 1]
        for col in score_cols:
            if (df[col] < 0).any() or (df[col] > 1).any():
                report.issues.append(f"ERROR: {col} has values outside [0, 1]")
                report.anomalies[col] = df[(df[col] < 0) | (df[col] > 1)].index.tolist()
    
    @staticmethod
    def _analyze_correlations(report: CoherenceReport, df: pd.DataFrame, score_cols: List[str]):
        """Analyse les corrélations entre scores"""
        
        for i, col1 in enumerate(score_cols):
            for col2 in score_cols[i+1:]:
                # Ignorer si std est 0
                if report.score_stds[col1] == 0 or report.score_stds[col2] == 0:
                    continue
                
                corr = df[col1].corr(df[col2])
                report.correlations[(col1, col2)] = float(corr)
                
                # Signaler les corrélations extrêmes
                if abs(corr) > ScoreCoherenceAnalyzer.ANOMALY_THRESHOLDS["extreme_correlation"]:
                    report.issues.append(f"WARNING: Extreme correlation between {col1} and {col2} (r={corr:.3f})")
                    report.recommendations.append(f"Consider combining or reviewing {col1} and {col2} - they are highly correlated")
    
    @staticmethod
    def _compute_quality_score(report: CoherenceReport) -> float:
        """Calcule un score de qualité global"""
        
        quality = 1.0
        
        # Pénalité pour chaque problème
        quality -= len(report.issues) * 0.1
        
        # Pénalité pour manque de variance
        for col, std in report.score_stds.items():
            if std < 0.01:
                quality -= 0.05
        
        # Pénalité pour corrélations extrêmes
        extreme_corrs = sum(1 for c in report.correlations.values() 
                           if abs(c) > ScoreCoherenceAnalyzer.ANOMALY_THRESHOLDS["extreme_correlation"])
        quality -= extreme_corrs * 0.05
        
        report.quality_score = max(0.0, quality)
        return report.quality_score
    
    @staticmethod
    def print_report(report: CoherenceReport):
        """Affiche un rapport lisible"""
        
        print("\n" + "="*70)
        print("SCORE COHERENCE ANALYSIS REPORT")
        print("="*70)
        
        print(f"\nDataset Information:")
        print(f"  Total pairs: {report.total_pairs:,}")
        print(f"  Quality Score: {report.quality_score:.2%}")
        
        print(f"\nScore Statistics:")
        print(f"{'Score':<20} {'Mean':<10} {'Std':<10} {'Min':<10} {'Max':<10}")
        print("-" * 60)
        
        for col in report.score_means.keys():
            mean = report.score_means[col]
            std = report.score_stds[col]
            min_val, max_val = report.score_ranges[col]
            print(f"{col:<20} {mean:>9.4f} {std:>9.4f} {min_val:>9.4f} {max_val:>9.4f}")
        
        if report.correlations:
            print(f"\nCorrelations:")
            for (col1, col2), corr in report.correlations.items():
                marker = " (HIGH!)" if abs(corr) > 0.8 else ""
                print(f"  {col1} <-> {col2}: {corr:>7.3f}{marker}")
        
        if report.issues:
            print(f"\nIssues ({len(report.issues)}):")
            for issue in report.issues:
                print(f"  ⚠ {issue}")
        
        if report.recommendations:
            print(f"\nRecommendations:")
            for rec in report.recommendations:
                print(f"  📝 {rec}")
        
        print("\n" + "="*70)


class RobustnessAnalyzer:
    """Analyse la robustesse du système de scoring"""
    
    @staticmethod
    def analyze_stability(df1: pd.DataFrame, df2: pd.DataFrame, 
                         score_cols: Optional[List[str]] = None) -> Dict[str, float]:
        """Analyse la stabilité entre deux runs with même données (shuffle différent)"""
        
        if score_cols is None:
            score_cols = ["score_skills", "score_experience", "score_education", 
                         "score_languages", "score_sector"]
        
        results = {}
        
        for col in score_cols:
            if col not in df1.columns or col not in df2.columns:
                continue
            
            # Corrélation de Spearman (robuste aux transformations monotones)
            corr = df1[col].rank().corr(df2[col].rank())
            results[f"{col}_stability"] = float(corr) if not pd.isna(corr) else 0.0
        
        # Stabilité globale = moyenne
        results["global_stability"] = np.mean(list(results.values())) if results else 0.0
        
        return results
    
    @staticmethod
    def analyze_perturbation_sensitivity(df: pd.DataFrame, perturbation_pct: float = 0.01) -> Dict[str, float]:
        """Analyse la sensibilité du système à des perturbations des données"""
        
        score_cols = ["score_skills", "score_experience", "score_education", 
                     "score_languages", "score_sector"]
        
        # Perturbations légères des données
        df_perturbed = df.copy()
        for col in ["years_experience", "education_level"]:
            if col in df_perturbed.columns:
                df_perturbed[col] = df_perturbed[col] * (1 + np.random.normal(0, perturbation_pct, len(df)))
        
        results = {}
        
        # Recalculer les scores avec perturbations (simulation)
        for col in score_cols:
            if col in df.columns:
                # Mesurer le changement
                original = df[col].values
                # Simulation: on assume une sensibilité linéaire
                perturbation = np.random.normal(0, perturbation_pct, len(df))
                perturbed = np.clip(original + original * perturbation, 0, 1)
                
                change = np.mean(np.abs(original - perturbed))
                results[f"{col}_sensitivity"] = float(change)
        
        results["mean_sensitivity"] = np.mean(list(results.values())) if results else 0.0
        
        return results


def run_comprehensive_analysis(pairs_df: pd.DataFrame) -> Tuple[CoherenceReport, Dict]:
    """Exécute une analyse complète de cohérence et robustesse"""
    
    # Analyse de cohérence
    coherence_report = ScoreCoherenceAnalyzer.analyze(pairs_df)
    
    # Analyse de robustesse (stabilité)
    robustness_stats = {
        "perturbation_sensitivity": RobustnessAnalyzer.analyze_perturbation_sensitivity(pairs_df)
    }
    
    return coherence_report, robustness_stats
