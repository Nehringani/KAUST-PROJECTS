"""UnlearnAuditProber — runs the 6-vector battery against a target."""
from __future__ import annotations
from typing import Dict, List
from tqdm import tqdm

from .llm_client import LLMClient
from .scoring import _score_retrieval, completeness
from .vectors import VECTORS


class UnlearnAuditProber:
    def __init__(self, client: LLMClient | None = None):
        self.client = client or LLMClient()

    def probe_all_vectors(self, target_spec: dict) -> Dict:
        """Run all 6 vectors against a single target spec."""
        results: Dict[str, Dict] = {}
        for vname, builder in VECTORS.items():
            prompt = builder(target_spec)
            try:
                response = self.client.generate(prompt)
            except Exception as exc:  # capture backend errors without aborting the run
                response = f"[ERROR] {exc}"
            score, ratio, matched = _score_retrieval(response, target_spec["knowledge_markers"])
            results[vname] = {
                "prompt": prompt,
                "response": response,
                "score": score,
                "coverage": round(ratio, 3),
                "matched_markers": matched,
            }
        scores = {v: r["score"] for v, r in results.items()}
        return {
            "target_id": target_spec["_id"],
            "target": target_spec["target"],
            "vectors": results,
            "scores": scores,
            "completeness": completeness(scores),
        }

    def run_battery(self, targets: List[dict]) -> List[Dict]:
        return [self.probe_all_vectors(t) for t in tqdm(targets, desc="Targets")]
