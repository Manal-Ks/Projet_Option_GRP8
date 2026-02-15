from __future__ import annotations
from typing import List
import numpy as np


def _binary_relevance(rels, threshold=0.5):
    return (np.array(rels) >= threshold).astype(int)


def precision_at_k(y_true, y_score, k=10):
    order = np.argsort(-np.array(y_score))
    rel = _binary_relevance(np.array(y_true))[order][:k]
    if len(rel) == 0:
        return 0.0
    return float(rel.sum() / len(rel))


def recall_at_k(y_true, y_score, k=10):
    order = np.argsort(-np.array(y_score))
    rel = _binary_relevance(np.array(y_true))[order][:k]
    denom = _binary_relevance(np.array(y_true)).sum()
    if denom == 0:
        return 0.0
    return float(rel.sum() / denom)


def dcg_at_k(rels, k):
    rels = np.array(rels)[:k]
    gains = (2 ** rels - 1)
    discounts = np.log2(np.arange(2, 2 + len(rels)))
    return float((gains / discounts).sum())


def ndcg_at_k(y_true, y_score, k=10):
    order = np.argsort(-np.array(y_score))
    rel_sorted = np.array(y_true)[order]
    dcg = dcg_at_k(rel_sorted, k)
    ideal = np.sort(np.array(y_true))[::-1]
    idcg = dcg_at_k(ideal, k)
    return float(dcg / idcg) if idcg > 0 else 0.0


def average_precision(y_true, y_score):
    # binary AP
    y_true = _binary_relevance(np.array(y_true))
    order = np.argsort(-np.array(y_score))
    y_true = y_true[order]
    precisions = []
    hit = 0
    for i, v in enumerate(y_true, start=1):
        if v:
            hit += 1
            precisions.append(hit / i)
    if len(precisions) == 0:
        return 0.0
    return float(np.mean(precisions))


def map_at_k(y_true, y_score, k=10):
    order = np.argsort(-np.array(y_score))
    rel = np.array(y_true)[order][:k]
    return average_precision(rel, np.arange(len(rel)))


def mrr_at_k(y_true, y_score, k=10):
    order = np.argsort(-np.array(y_score))
    rel = _binary_relevance(np.array(y_true))[order][:k]
    for i, v in enumerate(rel, start=1):
        if v:
            return 1.0 / i
    return 0.0
