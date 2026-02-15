import pandas as pd
import numpy as np

from src.scoring_engine.components.subscores import (
    skills_jaccard,
    experience_score,
    education_score,
    languages_score,
    sector_score,
)


def test_subscores_basic():
    assert skills_jaccard(["a", "b"], ["b", "c"]) == 1 / 3
    assert skills_jaccard([], ["a"]) == 0.0
    assert 0.0 <= experience_score(5, 3) <= 1.0
    assert education_score(5, 3) == 1.0
    assert education_score(2, 4) >= 0.0
    assert languages_score(["en", "fr"], ["en"]) == 1.0
    assert sector_score("it_data", "it_data") == 1.0
    assert sector_score(None, "it_data") == 0.0
