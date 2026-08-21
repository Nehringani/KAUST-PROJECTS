"""
Step 3 — Semantic clustering with SentenceTransformer + KMeans.

Falls back to TF-IDF + KMeans if `sentence-transformers` cannot be loaded
(e.g. no network on first run). Cluster labels are renamed by dominant class.
"""
from __future__ import annotations

import logging
from typing import Tuple

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans

from .taxonomy import CLASS_KEYS

log = logging.getLogger(__name__)


def _embed(texts: list[str], model_name: str) -> np.ndarray:
    try:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer(model_name)
        return np.asarray(model.encode(texts, show_progress_bar=False, batch_size=64))
    except Exception as exc:
        log.warning("SentenceTransformer unavailable (%s). Falling back to TF-IDF.", exc)
        from sklearn.feature_extraction.text import TfidfVectorizer
        vec = TfidfVectorizer(max_features=2048, ngram_range=(1, 2))
        return vec.fit_transform(texts).toarray()


def cluster(df: pd.DataFrame, n_clusters: int = 8, model_name: str = "all-MiniLM-L6-v2",
            seed: int = 42) -> Tuple[pd.DataFrame, dict[int, str]]:
    """Return (df with `cluster` and `cluster_label`, cluster_id -> dominant class map)."""
    emb = _embed(df["prompt"].tolist(), model_name)
    km = KMeans(n_clusters=n_clusters, random_state=seed, n_init=10)
    labels = km.fit_predict(emb)

    out = df.copy()
    out["cluster"] = labels

    # Rename each cluster after its dominant taxonomy class.
    mapping: dict[int, str] = {}
    for cid in range(n_clusters):
        subset = out.loc[out["cluster"] == cid, "class"]
        if subset.empty:
            mapping[cid] = CLASS_KEYS[cid % len(CLASS_KEYS)]
        else:
            mapping[cid] = subset.mode().iloc[0]
    out["cluster_label"] = out["cluster"].map(mapping)
    return out, mapping
