# Projet_Option_GRP8 : Pipeline de Jumelage Candidat-Offre + Dashboard RH Interactif

## Table des Matières

* [Vue d'ensemble](#vue-densemble)
* [Prérequis](#prérequis)
* [Architecture du Projet](#architecture-du-projet)
* [Installation Complète](#installation-complète)
* [Guide d'Utilisation](#guide-dutilisation)
* [Exécution des Tests](#exécution-des-tests)
* [Expériences de Scoring](#expériences-de-scoring)
* [Dashboard RH (Streamlit + Plotly)](#dashboard-rh-streamlit--plotly)
* [Structure des Données](#structure-des-données)
* [Documentation Technique](#documentation-technique)
* [Dépannage](#dépannage)

---

## Vue d'ensemble

Le projet **Projet_Option_GRP8** est un pipeline complet et production-ready de jumelage candidat-offre d’emploi, enrichi d’un **dashboard RH interactif** permettant de **simuler des priorités de recrutement (poids)** et de visualiser les meilleurs matches par poste.

Le système fournit :

* **Validation de données** : schéma strict pour les entrées CSV (candidats et offres)
* **Prétraitement** : normalisation texte, parsing de listes, application de domaines spécialisés, gestion NA, coercion types
* **Normalisation de domaines** : éducation, langues, compétences, secteur d'activité
* **Vérification de qualité** : rapports détaillés (complétude, couverture, champs critiques)
* **Jumelage** : génération de paires candidat-emploi (cartésien ou filtré)
- **Intelligence de scoring** : 6 algorithmes de scoring pour l'évaluation des matches
* **Subscores explicables** : 5 sous-scores normalisés ([0,1])
* **Orchestration Pipeline** : `run()` (load → preprocess → pairing → subscores → agrégation → export)
* **Export final** : `results/pairs_scored.csv` (avec `vector_score` + `global_score`)
* **Dashboard RH** : shortlist par poste, fiche candidat, comparaison A/B, pondération dynamique live

Le pipeline est conçu pour être **modulaire, testable et scalable** avec une couverture de tests unitaires et end-to-end.

---

## Prérequis

### Système d'Exploitation

* **Windows** (recommandé)
* macOS / Linux (support limité)

### Logiciels Requis

| Composant | Version Minimale | Version Testée |
| --------- | ---------------- | -------------- |
| Python    | 3.8             | 3.10.11         |
| pip       | 20.0+            | 26.0.1           |

> Recommandation : éviter de mélanger Anaconda et `venv`. Utiliser **un seul** environnement (venv recommandé).

### Dépendances Python

Toutes les dépendances sont spécifiées dans `requirements.txt` :

```txt
pandas>=2.0
numpy>=1.24
pyyaml>=6.0
pytest>=7.0
scikit-learn>=1.2
streamlit>=1.30
plotly>=5.18
```

---

## Architecture du Projet

### Structure des Répertoires
```
Projet_Option_GRP8/
├── demo_dev_run.py                    # Script de démonstration principal (DEV dataset)
├── demo_part1.py                      # Démonstration partielle (Phase 1 : Data Layer)
├── tmp_smoke.py                       # Tests de fumée (smoke tests)
├── pyproject.toml                     # Configuration de build Python
├── requirements.txt                   # Dépendances du projet (inclut streamlit + plotly)
├── config.yaml                        # Configuration pipeline (poids + options pairing/export)
├── README.md                          # Cette documentation
│
├── dashboard/                         # Dashboard RH interactif (Streamlit + Plotly)
│   └── app.py                         # App finale : shortlist, fiche candidat, comparaison A/B, poids live
│
├── src/                               # Code source principal
│   ├── __init__.py
│   ├── schema.py                      # Schémas de validation des entrées
│   ├── preprocessing.py               # Pipeline de prétraitement
│   ├── data_layer.py                  # Orchestration Data Layer (validate → preprocess → QC → pairing)
│   ├── data_quality.py                # Rapports de qualité
│   ├── pairing.py                     # Génération des paires candidat-emploi (cartesian / same_sector)
│   ├── education.py                   # Normalisation de l'éducation
│   ├── languages.py                   # Normalisation des langues
│   ├── skills.py                      # Normalisation des compétences
│   ├── sector.py                      # Normalisation du secteur
│   ├── pipeline.py                    # Orchestration globale (run: data_layer → subscores → aggregate → export)
│   ├── aggregate.py                   # Calcul vector_score + global_score pondéré (configurable)
│   └── export.py                      # Export des résultats (CSV/JSON) vers results/
│   │
│   └── scoring_engine/                # Moteur de scoring avancé
│       ├── __init__.py
│       ├── config.py                  # Configuration globale scoring (si utilisé par les expériences)
│       ├── evaluation.py              # Calcul des subscores en dataframe (compute_subscores_df)
│       ├── components/
│       │   └── subscores.py           # Fonctions de scoring : skills/exp/edu/lang/sector ∈ [0,1]
│       ├── algorithms/
│       │   ├── base.py                # Classe de base abstraite
│       │   └── algorithms.py          # Algorithmes de scoring (WSM, WPM, TOPSIS, LR, RF, GB)
│       └── metrics/
│           └── ranking_metrics.py     # Métriques de ranking (P@K, NDCG, etc.)
│
├── tests/                             # Suite de tests complète
│   ├── test_data_layer.py             # Tests de la couche données
│   ├── test_data_layer_api.py         # Tests API de la couche données
│   ├── test_preprocessing_normalizers.py # Tests des normalisateurs
│   ├── test_scoring_e2e.py            # Tests end-to-end (pipeline + scoring)
│   ├── test_scoring_unit.py           # Tests unitaires des subscores
│   └── README.md                      # Documentation des tests
│
├── data/                              # Données du projet
│   ├── dev/                           # Jeu de données de développement
│   │   ├── candidates_dev.csv         # 10,000 candidats
│   │   ├── jobs_dev.csv               # 200 offres d'emploi
│   │   └── README.md
│   ├── samples/                       # Jeu d'échantillons (petit)
│   │   ├── candidates_sample.csv
│   │   ├── jobs_sample.csv
│   │   └── README.md
│   └── test/                          # Données de test
│       └── README.md
│
├── scripts/                           # Utilitaires et scripts
│   ├── setup_venv_windows.bat         # Configuration de l'environnement
│   ├── run_demo_windows.bat           # Lancement de la démo
│   ├── test_windows.bat               # Exécution des tests
│   ├── run_scoring_experiments.py     # Expériences de scoring (leaderboard + topK)
│   └── generate_dev_data.py           # Génération de données de dev
│
├── docs/                              # Documentation technique
│   ├── architecture.md                # Détails architecturaux
│   └── data_contract.md               # Contrat de données (schémas)
│
└── results/                           # Résultats (pipeline + dashboard + expériences)
    ├── pairs_scored.csv               # Output pipeline : scores + vector_score + global_score
    ├── leaderboard.csv                # Classement des algorithmes (expériences)
    ├── best_algo_top10.csv            # Top 10 du meilleur algorithme
    └── config_used.json               # Configuration utilisée (expériences)
```

### Composants Clés

#### 1) Couche Schéma (`src/schema.py`)

* Définit les schémas candidats / jobs
* Valide + coercion des types
* Garantit la compatibilité pipeline

#### 2) Prétraitement (`src/preprocessing.py`)

* Normalisation texte (accents/casse/espaces)
* Parsing listes (skills/langues)
* Nettoyage robuste et reproductible

#### 3) **Normalisateurs de Domaine**
- `education.py` : Mappe les diplômes à niveaux numériques
- `languages.py` : Normalise les langues, calcule les chevauchements
- `skills.py` : Normalise les compétences, harmonise la nomenclature
- `sector.py` : Normalise les secteurs, vérifie l'alignement

#### 4) Couche Données (`src/data_layer.py`)

Orchestration Data Layer :

1. Validation
2. Prétraitement
3. Rapports qualité
4. Pairing (cartésien / filtré)

Retourne :

* `pairs_df`
* `qc_candidates`
* `qc_jobs`
#### 5) **Moteur de Scoring** (`src/scoring_engine/`)
- **6 Algorithmes** : WSM, WPM, TOPSIS, LogisticRegression, RandomForest, GradientBoosting
- **Métriques** : P@K, Recall@K, NDCG@K, MAP@K, MRR@K
- **Évaluation** : Cross-validation par candidat

#### 6) Subscores Engine (`src/scoring_engine/components/subscores.py`)

* Calcule 5 sous-scores ([0,1]) :

  * `score_skills`, `score_experience`, `score_education`, `score_languages`, `score_sector`

#### 7) Pipeline Orchestration (`src/pipeline.py`)

* Assemble tout le système via `run()`
* Produit un dataframe final + exports

---

## Installation Complète

### Étape 1 : Accès au projet

###  Clonage depuis GitHub

Le projet est disponible sur le repository officiel :

```
https://github.com/Manal-Ks/Projet_Option_GRP8.git
```

### Étape 1 — Cloner le repository

```bash
git clone https://github.com/Manal-Ks/Projet_Option_GRP8.git
```

### Étape 2 — Se placer dans le dossier du projet

```bash
cd Projet_Option_GRP8
```



### Étape 2 : Création + activation venv

```powershell
python -m venv .venv
.\.venv\Scripts\activate
```
# Sur macOS/Linux
source .venv/bin/activate
### Étape 3 : Upgrade pip + install deps

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### Étape 4 : Vérification

```powershell
python -c "import pandas, numpy, yaml, streamlit, plotly; print('OK')"
```
**Résultat attendu** : 
```
numpy                    2.2.6
pandas                   2.3.3
pytest                   9.0.2
scikit-learn             1.7.2
```

---

## Guide d'Utilisation

### Usage 1 : Lancer le pipeline (CSV → résultats)

Dans un terminal **avec venv activé** :

```powershell
python
```

Puis dans le REPL Python :

```python
import pandas as pd
from src.pipeline import run

df_cv = pd.read_csv("data/samples/candidates_sample.csv")
df_jobs = pd.read_csv("data/samples/jobs_sample.csv")

out, meta = run(df_cv, df_jobs, config_path="config.yaml", export=True)

print(out.head())
print(meta["quality_report"].keys())  # candidates / jobs
```

 Résultat attendu :

* `out` contient `score_*`, `vector_score`, `global_score`
* Export automatique dans `results/pairs_scored.csv`

---

### Usage 2 : Vérifier rapidement les bornes des scores

```python
assert out["global_score"].between(0, 1).all()

# pandas ne supporte pas DataFrame.between, donc on fait colonne par colonne :
for c in ["score_skills","score_experience","score_education","score_languages","score_sector"]:
    assert out[c].between(0, 1).all()
print("OK: scores bornés [0,1]")
```

---

## Exécution des Tests

### Suite complète

```powershell
python -m pytest -v
```

### Modules ciblés

```powershell
python -m pytest tests/test_data_layer.py -v
python -m pytest tests/test_scoring_unit.py -v
python -m pytest tests/test_scoring_e2e.py -v
```

---

## Expériences de Scoring

Le projet supporte des expériences comparant plusieurs algorithmes (WSM/WPM/TOPSIS/ML…).

Exécution (si disponible dans `scripts/`) :

```powershell
python scripts\run_scoring_experiments.py
```

Sorties typiques :

* `results/leaderboard.csv`
* `results/best_algo_top10.csv`
* `results/config_used.json`

---

## Dashboard RH (Streamlit + Plotly)

Le dashboard transforme le moteur en **plateforme décisionnelle RH** :

* Shortlist par poste
* Pondération dynamique live (priorités recrutement)
* KPI instantanés
* Radar chart (profil de match)
* Fiche candidat (top jobs)
* Comparaison A/B sur un poste (graph miroir Plotly)

### Lancement

```powershell
streamlit run dashboard/app.py
```

### Fonctionnement des poids (priorités recrutement)

Dans la sidebar :

* 5 sliders (0 à 10) : Compétences, Expérience, Formation, Langues, Secteur
* Normalisation automatique (somme = 1)
* Recalcul instantané d’un score dynamique :

`score_live = Σ (score_i × weight_i)` puis clipping ([0,1])

> Les poids sont appliqués au **poste sélectionné** (shortlist du job).

---

## Structure des Données

### Entrée : Candidats (`candidates_*.csv`)

Colonnes typiques :

* `candidate_id`
* `skills` (liste)
* `languages` (liste)
* `education_level` / `candidate_level` (selon schéma)
* `years_experience`
* `sector`

### Entrée : Offres (`jobs_*.csv`)

Colonnes typiques :

* `job_id`
* `required_skills` (liste)
* `required_languages` (liste)
* `required_education` / `job_level`
* `min_experience`
* `required_sector`

### Sortie pipeline : `results/pairs_scored.csv`

Colonnes finales :

* `candidate_id`, `job_id`
* `sector`, `required_sector`
* `score_skills`, `score_experience`, `score_education`, `score_languages`, `score_sector`
* `global_score`
* `vector_score` (liste des 5 sous-scores)

---

## Documentation Technique

* `docs/architecture.md` : architecture / design (si disponible)
* `docs/data_contract.md` : contrat de données / schémas (si disponible)

### Formules des sous-scores (résumé)

* Skills (Jaccard) : (|A∩B| / |A∪B|)
* Languages (coverage) : (|A∩B| / |B|)
* Education : (1) si candidat ≥ requis sinon ((cand/job)^2)
* Sector : 1 (match) / 0.5 (mismatch)
* Global : somme pondérée

---

## Dépannage

### 1) `from src...` ne marche pas dans PowerShell
 Normal : c’est une commande Python, pas PowerShell.

Solution :

```powershell
python
```

Puis :

```python
from src.pipeline import run
```

### 2) `No module named 'src'`

Lancer depuis la racine du projet :

```powershell
cd Projet_Option_GRP8
python -c "import src"
```

### 3) Conflit Anaconda / venv

Symptôme : python pointe vers Anaconda.

Vérifie :

```powershell
where python
```

Attendu :

* `...\Projet_Option_GRP8\.venv\Scripts\python.exe`

Si ce n’est pas le cas :

* ferme le terminal
* réactive `.venv`
* évite `conda activate` en même temps

### 4) `ImportError compute_subscores`

Vérifier que `compute_subscores_df` est importé depuis `src.scoring_engine.evaluation` (et non l’inverse), et que `subscores.py` expose bien les fonctions de base.

### 5) Performance lente

Cause : pairing cartésien (N×M).

Mitigation :

* utiliser `pairing_mode="same_sector"`
* réduire datasets pour itération
* batch / filtrage en amont

---

**Dernière mise à jour** : 16 février 2026
**Version** : 2.0 (Pipeline + Dashboard RH Interactif)
**Statut** :  Pipeline opérationnel + Dashboard Streamlit final
