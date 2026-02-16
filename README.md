# Projet_Option_GRP8 : Pipeline de Jumelage Candidat-Offre d'Emploi

## Table des Matières
- [Vue d'ensemble](#vue-densemble)
- [Prérequis](#prérequis)
- [Architecture du Projet](#architecture-du-projet)
- [Installation Complète](#installation-complète)
- [Guide d'Utilisation](#guide-dutilisation)
- [Exécution des Tests](#exécution-des-tests)
- [Expériences de Scoring](#expériences-de-scoring)
- [Structure des Données](#structure-des-données)
- [Documentation Technique](#documentation-technique)
- [Dépannage](#dépannage)

---

## Vue d'ensemble

Le projet **Projet_Option_GRP8** est un pipeline complet et production-ready de jumelage candidat-offre d'emploi. Il fournit :

- **Validation de données** : Schéma stricte pour les entrées CSVs (candidats et offres)
- **Prétraitement** : Normalisation du texte, parsing de listes, application de domaines spécialisés
- **Normalisation de domaines** : Education, langues, compétences, secteur d'activité
- **Vérification de qualité** : Rapports détaillés sur la couverture et complétude des données
- **Jumelage** : Génération de paires candidat-emploi en modes cartésien ou filtré
- **Intelligence de scoring** : 6 algorithmes de scoring pour l'évaluation des matches

Le pipeline est conçu pour être **modulaire, testable et scalable** avec une couverture complète de tests unitaires et end-to-end.

---

## Prérequis

### Système d'Exploitation
- **Windows** (recommandé pour ce projet)
- **macOS** ou **Linux** (support limité)

### Logiciels Requis
| Composant | Version Minimale | Version Testée |
|-----------|-----------------|----------------|
| Python | 3.8 | 3.10.11 |
| pip | 20.0+ | 26.0.1 |

### Dépendances Python
Toutes les dépendances sont spécifiées dans [requirements.txt](requirements.txt) :

```
pandas>=2.0          # Manipulation et analyse de données
numpy>=1.24          # Calculs numériques
pyyaml>=6.0          # Sérialisation YAML
pytest>=7.0          # Framework de tests
scikit-learn>=1.2    # Machine Learning et métriques
```

### Espace Disque
- Environnement virtuel : ~500 MB
- Données de développement : ~100 MB (optionnel)
- Résultats des expériences : ~10 MB

---

## Architecture du Projet

### Structure des Répertoires

```
Projet_Option_GRP8/
├── demo_dev_run.py                    # Script de démonstration principal
├── demo_part1.py                      # Démonstration partielle (Phase 1)
├── tmp_smoke.py                       # Tests de fumée (smoke tests)
├── pyproject.toml                     # Configuration de build Python
├── requirements.txt                   # Dépendances du projet
├── README.md                          # Cette documentation
│
├── src/                               # Code source principal
│   ├── __init__.py
│   ├── schema.py                      # Schémas de validation des entrées
│   ├── preprocessing.py               # Pipeline de prétraitement
│   ├── data_layer.py                  # Orchestration de la couche données
│   ├── data_quality.py                # Rapports de qualité
│   ├── pairing.py                     # Génération des paires candidat-emploi
│   ├── education.py                   # Normalisation de l'éducation
│   ├── languages.py                   # Normalisation des langues
│   ├── skills.py                      # Normalisation des compétences
│   ├── sector.py                      # Normalisation du secteur
│   │
│   └── scoring_engine/                # Moteur de scoring avancé
│       ├── __init__.py
│       ├── config.py                  # Configuration globale
│       ├── evaluation.py              # Pipeline d'évaluation
│       ├── components/
│       │   └── subscores.py           # Calcul des sous-scores
│       ├── algorithms/
│       │   ├── base.py                # Classe de base abstraite
│       │   └── algorithms.py          # 6 algorithmes de scoring
│       └── metrics/
│           └── ranking_metrics.py     # Métriques de ranking (P@K, NDCG, etc.)
│
├── tests/                             # Suite de tests complète
│   ├── test_data_layer.py             # Tests de la couche données
│   ├── test_data_layer_api.py         # Tests API de la couche données
│   ├── test_preprocessing_normalizers.py # Tests des normalisateurs
│   ├── test_scoring_e2e.py            # Tests end-to-end du scoring
│   ├── test_scoring_unit.py           # Tests unitaires du scoring
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
│   ├── run_scoring_experiments.py     # Expériences de scoring
│   └── generate_dev_data.py           # Génération de données de dev
│
├── docs/                              # Documentation technique
│   ├── architecture.md                # Détails architecturaux
│   └── data_contract.md               # Contrat de données (schémas)
│
└── results/                           # Résultats des expériences
    ├── leaderboard.csv                # Classement des algorithmes
    ├── best_algo_top10.csv            # Top 10 du meilleur algorithme
    └── config_used.json               # Configuration utilisée
```

### Composants Clés

#### 1. **Couche de Schéma** (`src/schema.py`)
- Définit les schémas de validation pour candidats et offres
- Valide et transforme les données entrantes
- Gère la coercion de types

#### 2. **Couche de Prétraitement** (`src/preprocessing.py`)
- Normalise le texte (accents, casse, espaces)
- Parse les listes formatées en chaînes
- Applique les normalisateurs de domaine

#### 3. **Normalisateurs de Domaine**
- `education.py` : Mappe les diplômes à niveaux numériques
- `languages.py` : Normalise les langues, calcule les chevauchements
- `skills.py` : Normalise les compétences, harmonise la nomenclature
- `sector.py` : Normalise les secteurs, vérifie l'alignement

#### 4. **Couche de Données** (`src/data_layer.py`)
Orchestration complète :
1. Validation des entrées
2. Prétraitement
3. Vérification qualité
4. Génération des paires

#### 5. **Moteur de Scoring** (`src/scoring_engine/`)
- **6 Algorithmes** : WSM, WPM, TOPSIS, LogisticRegression, RandomForest, GradientBoosting
- **Métriques** : P@K, Recall@K, NDCG@K, MAP@K, MRR@K
- **Évaluation** : Cross-validation par candidat

---

## Installation Complète

### Étape 1 : Clonage / Récupération du Projet

```bash
# Accédez au répertoire souhaité
cd "c:\Users\SAMI YOUSSEF\OneDrive\Desktop\Option_3A\"

# Le projet est déjà présent dans : Projet_Option_GRP8/
cd Projet_Option_GRP8
```

### Étape 2 : Vérification de Python

Vérifiez que Python 3.8+ est installé et accessible :

```bash
python --version
```

**Résultat attendu** : `Python 3.10.11` (ou supérieur)

### Étape 3 : Création de l'Environnement Virtuel

L'environnement virtuel isole les dépendances du projet de votre système :

```bash
# Créer l'environnement virtuel
python -m venv .venv

# Activer l'environnement (Windows)
.\.venv\Scripts\activate.bat

# Sur macOS/Linux
source .venv/bin/activate
```

**Indicateur d'activation** : Votre prompt commence par `(.venv)`

### Étape 4 : Mise à Niveau de pip

```bash
python -m pip install --upgrade pip
```

**Résultat attendu** : Confirmation que pip a été mis à niveau

### Étape 5 : Installation des Dépendances

```bash
# Installez toutes les dépendances spécifiées
python -m pip install -r requirements.txt
```

**Vérification** : Aucun message d'erreur ne doit apparaître

### Étape 6 : Vérification Installation

```bash
# Vérifiez que les packages sont installés
python -m pip list | findstr /i "pandas numpy pytest scikit"
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

### Configuration Recommandée

Pour tous les scripts, utilisez l'environnement virtuel activé :

```bash
cd Projet_Option_GRP8
.\.venv\Scripts\activate
```

### Usage 1 : Démonstration Simple (Données Petites)

Pour un test rapide avec des données d'échantillon :

```bash
python demo_part1.py
```

**Temps d'exécution** : < 5 secondes

**Résultat** : Affiche les étapes de validation et quelques paires

### Usage 2 : Démonstration Complète (Données de Développement)

Pour un test complet avec 10,000 candidats et 200 offres :

```bash
python demo_dev_run.py
```

**Temps d'exécution** : 15-30 secondes

**Résultats affichés** :
```
Using DEV dataset.

--- Counts ---
candidates: 10000
jobs      : 200
pairs     : 2000000

--- Quality report (candidates) ---
n_rows: 10000
pct_empty_skills: 0.0
pct_missing_languages: 0.0293
pct_missing_sector: 0.0111
pct_missing_education: 0.0107

--- Quality report (jobs) ---
n_rows: 200
pct_empty_required_skills: 0.0
pct_empty_required_languages: 0.0
pct_missing_required_sector: 0.0
pct_missing_required_education: 0.0

--- Sample pairs ---
  candidate_id  ...  required_skills
0      C000001  ...  [due_diligence, audit, consolidation, presenta...

[3 rows x 6 columns]
```

### Usage 3 : Utilisation Programmée

Intégrez le pipeline dans votre code :

```python
from src.data_layer import prepare_data_layer
import pandas as pd

# Chargez vos données
candidates = pd.read_csv("data/samples/candidates_sample.csv")
jobs = pd.read_csv("data/samples/jobs_sample.csv")

# Lancez le pipeline complet
pairs, quality_report = prepare_data_layer(
    candidates, 
    jobs, 
    pairing_mode="cartesian"  # ou "filtered_same_sector"
)

# Exploitez les résultats
print(f"Generated {len(pairs)} pairs")
print(f"Quality: {quality_report}")
```

### Usage 4 : Tests de Fumée

Pour identifier rapidement les regressions :

```bash
python tmp_smoke.py
```

---

## Exécution des Tests

### Test Rapide (Approche Recommandée)

```bash
python -m pytest -v
```

**Résultat attendu** : 
```
============================= 7 passed in 2.29s =============================
```

### Test Avec Couverture Détaillée

```bash
python -m pytest -v --tb=short
```

### Test d'un Module Spécifique

```bash
# Tester uniquement la couche données
python -m pytest tests/test_data_layer.py -v

# Tester uniquement les normalisateurs
python -m pytest tests/test_preprocessing_normalizers.py -v

# Tester uniquement le scoring
python -m pytest tests/test_scoring_unit.py tests/test_scoring_e2e.py -v
```

### Résultats des Tests

**Suite complète** : 7 tests
- ✅ `test_schema_and_preprocess` : Validation et prétraitement
- ✅ `test_pairing_cartesian_shape` : Jumelage cartésien
- ✅ `test_to_list_parses_python_list_string` : Parsing de listes
- ✅ `test_prepare_data_layer_returns_pairs_and_reports` : Pipeline complet
- ✅ `test_candidate_and_job_normalizers` : Normalisateurs de domaine
- ✅ `test_e2e_run` : Scoring end-to-end
- ✅ `test_subscores_basic` : Calcul des sous-scores

---

## Expériences de Scoring

### Objectif

Générer un jeu de données synthétique et évaluer 6 algorithmes de scoring pour identifier le meilleur.

### Exécution

```bash
python scripts\run_scoring_experiments.py
```

**Temps d'exécution** : 1-2 minutes (selon la machine)

**Résultat** : Création du répertoire `results/` avec 3 fichiers

### Fichiers Générés

#### 1. `results/leaderboard.csv`

Classement des algorithmes avec métriques agrégées :

```csv
algo,precision@k,recall@k,ndcg@k,map@k,mrr@k,runtime
GradientBoosting,0.5926,1.0,0.9678,0.4531,0.9556,0.0951
LogisticRegression,0.5926,1.0,0.9973,0.4469,1.0,0.0134
RandomForest,0.5926,1.0,0.9587,0.4499,1.0,0.0734
TOPSIS,0.5926,1.0,0.9973,0.4469,1.0,0.0004
WPM,0.5926,1.0,0.9974,0.4447,1.0,0.0015
WSM,0.5926,1.0,0.9974,0.4496,1.0,0.0004
```

**Interprétation** :
- **Recall@K = 1.0** : Tous les algorithmes trouvent tous les bons candidats
- **NDCG@K** : LogisticRegression et TOPSIS sont les plus performants (0.9973)
- **Runtime** : TOPSIS est le plus rapide (0.0004s)

#### 2. `results/best_algo_top10.csv`

Prédictions du meilleur algorithme pour les 10 meilleures paires

#### 3. `results/config_used.json`

Configuration utilisée pour les expériences

### Paramètres des Expériences

Éditables dans `scripts/run_scoring_experiments.py` :

```python
generate_synthetic(
    num_jobs=5,           # Nombre d'offres
    num_candidates=30,    # Nombre de candidats
    seed=42               # Graine aléatoire (reproductibilité)
)
```

---

## Structure des Données

### Format des Données d'Entrée

#### Candidats (`candidates_*.csv`)

```csv
candidate_id,candidate_name,skills,languages,education_level,years_experience,sector
C000001,John Doe,"[excel, python, leadership]","[english, french]",Master,5,Finance
C000002,Jane Smith,"[java, sql, agile]","[english]",Bachelor,3,IT
```

**Colonnes** :
| Colonne | Type | Description | Exemple |
|---------|------|-------------|---------|
| `candidate_id` | str | Identifiant unique | C000001 |
| `candidate_name` | str | Nom complet | John Doe |
| `skills` | list (string) | Compétences formatées liste-Python | [excel, python] |
| `languages` | list (string) | Langues parlées | [english, french] |
| `education_level` | str | Diplôme le plus élevé | Master, Bachelor |
| `years_experience` | int | Années d'expérience | 5 |
| `sector` | str | Secteur primaire | Finance, IT |

#### Offres d'Emploi (`jobs_*.csv`)

```csv
job_id,job_title,required_skills,required_languages,required_education,min_experience,required_sector
J000001,Senior Python Developer,"[python, sqlalchemy, fastapi]","[english]",Master,5,IT
J000002,Financial Analyst,"[excel, sql, tableau, vba]","[english, french]",Bachelor,3,Finance
```

**Colonnes** :
| Colonne | Type | Description | Exemple |
|---------|------|-------------|---------|
| `job_id` | str | Identifiant unique | J000001 |
| `job_title` | str | Titre du poste | Senior Python Developer |
| `required_skills` | list (string) | Compétences requises | [python, sqlalchemy] |
| `required_languages` | list (string) | Langues requises | [english] |
| `required_education` | str | Diplôme requis | Master, Bachelor |
| `min_experience` | int | Années minimum | 5 |
| `required_sector` | str | Secteur requis | IT |

### Format des Données Après Traitement

N'oubliez pas que après le pipeline, deux colonnes numériques sont ajoutées :

```csv
candidate_id,...,education_level,education_level_num,...
C000001,...,Master,4,...
```

- `education_level_num` : 0=Bac, 1=License, 2=Master, 3=PhD (etc.)
- `required_education_num` : Niveau requis (numérisé)

---

## Documentation Technique

### Documents Disponibles

1. [docs/architecture.md](docs/architecture.md)
   - Diagrammes de flux
   - Détails de chaque composant
   - Patterns de conception

2. [docs/data_contract.md](docs/data_contract.md)
   - Schémas complets
   - Règles de validation
   - Exemples de données

### Normalisation des Domaines

#### 1. Education (`src/education.py`)

**Niveaux reconnus** :
```python
{
    "high_school": 0,
    "diploma": 0,
    "bachelor": 1,
    "licence": 1,
    "master": 2,
    "mba": 2,
    "phd": 3,
    "doctorate": 3
}
```

#### 2. Langues (`src/languages.py`)

Détecte et normalise les codes de langue (fr, en, es, de, etc.)
Calcule le chevauchement entre candidats et offres.

#### 3. Compétences (`src/skills.py`)

Normalise les compétences contre un dictionnaire canonique.
- Python → python (minuscules)
- C++ → cpp
- VB.NET → vbnet

#### 4. Secteur (`src/sector.py`)

Mappe les secteurs à des catégories standard :
- IT, Finance, Healthcare, Manufacturing, etc.
- Vérifie l'alignement candidate-offre

### Algorithmes de Scoring

#### 1. **WSM** (Weighted Sum Model)
Score = Σ(poids × sous-scores)

#### 2. **WPM** (Weighted Product Model)
Score = ∏(sous-scores ^ poids)

#### 3. **TOPSIS** (Technique for Order Preference by Similarity to Ideal Solution)
Distance aux solutions idéale et non-idéale

#### 4. **Logistic Regression**
Modèle ML classique (entraîné sur les données de dev)

#### 5. **Random Forest**
Ensemble de 100 arbres de décision

#### 6. **Gradient Boosting**
Boosting gradient pour meilleure séparation

### Métriques d'Évaluation

Pour chaque offre d'emploi, on calcule :

- **Precision@K** : (vrais positifs) / K
- **Recall@K** : (vrais positifs) / (total positifs)
- **NDCG@K** : Normalized Discounted Cumulative Gain
- **MAP@K** : Mean Average Precision
- **MRR@K** : Mean Reciprocal Rank

Valeur par défaut : **K = 5**

---

## Dépannage

### Problème 1 : "No module named 'src'"

**Cause** : Script lancé hors du répertoire racine du projet

**Solution** :
```bash
cd Projet_Option_GRP8
python script_name.py
```

### Problème 2 : "ImportError: attempted relative import with no known parent package"

**Cause** : Import direct au lieu de passer par le package

**Solution** : Utilisez toujours :
```bash
python demo_dev_run.py  # Bon
python src/preprocessing.py  # Mauvais
```

### Problème 3 : "pandas: KeyError in operations"

**Cause** : Noms de colonnes incorrects ou manquants dans les données

**Solution** : Vérifiez les noms de colonnes des CSVs d'entrée

### Problème 4 : Tests échouent avec "NameError"

**Cause** : Mauvais import de fonction

**Solution** : Vérifiez que tous les imports utilisent les noms exacts

### Problème 5 : Performance lente

**Cause** : Fusion cartésienne (N × M paires)

**Mitigation** :
- Utilisez le mode "filtered_same_sector" pour réduire le nombre de paires
- Réduisez la taille des données de test
- Utilisez TOPSIS pour scoring rapide (< 1ms)

### Problème 6 : Environnement virtuel non activé

**Symptôme** : `pip` est le système pip, pas celui du projet

**Vérification** :
```bash
where python
# Doit afficher : C:\...\Projet_Option_GRP8\.venv\Scripts\python.exe
```

**Réactivation** :
```bash
.\.venv\Scripts\activate
```

---

## Scripts Disponibles

### Windows

```powershell
# Configuration automatisée
call scripts\setup_venv_windows.bat

# Lancement de la démo
call scripts\run_demo_windows.bat

# Exécution des tests
call scripts\test_windows.bat
```

### Cross-Platform

```bash
# Depuis n'importe quel OS
python demo_dev_run.py
python -m pytest -v
python scripts\run_scoring_experiments.py
```

---

## Fonctionnalités Clés Ajoutées

✅ **4 Modules de Normalisation** : education.py, languages.py, skills.py, sector.py

✅ **Pipeline Complet** : De la validation au scoring en passant par la qualité

✅ **6 Algorithmes de Scoring** : Approches heuristiques et ML

✅ **Tests Exhaustifs** : 7 tests couvrant tous les modules

✅ **Métriques Avancées** : P@K, NDCG@K, MAP@K, MRR@K

✅ **Expériences Reproductibles** : Graine aléatoire, configuration exportée

---

## Support et Maintenance

Pour toute question ou problème :

1. Consultez [docs/architecture.md](docs/architecture.md)
2. Vérifiez les tests dans [tests/README.md](tests/README.md)
3. Exécutez les tests de fumée : `python tmp_smoke.py`

---

**Dernière mise à jour** : 16 février 2026  
**Version** : 1.0  
**Statut** : ✅ Tous les tests passent