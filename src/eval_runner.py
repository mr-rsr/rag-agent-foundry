"""
Evaluation Runner for Azure AI Foundry Appliance Support Agent.
Loads datasets from Evals/ and calculates grounding, relevance, and citation adherence metrics.
"""

import os
import sys
import json
from pathlib import Path
from typing import List, Dict, Any

# Ensure UTF-8 output on Windows consoles
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

EVAL_DATASET_PATH = Path("Evals/appliance_support_evaluation.jsonl")

def load_eval_dataset(file_path: Path) -> List[Dict[str, Any]]:
    records = []
    if not file_path.exists():
        print(f"Error: Dataset not found at {file_path}")
        return records

    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def evaluate_dataset(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Computes heuristic benchmark scores across dataset records:
    - Citation Coverage: Checks if response contains expected source bracket citation (e.g., [*.pdf])
    - Grounding Match: Assesses overlap between ground truth key terms and response
    - Refusal Adherence: Checks appropriate limitation handling for out-of-domain queries
    """
    total = len(records)
    if total == 0:
        return {"total_records": 0}

    citation_hits = 0
    grounding_hits = 0
    refusal_hits = 0

    print(f"\nRunning Evaluation on {total} sample records...")
    print("-" * 65)

    for idx, item in enumerate(records, 1):
        query = item.get("query", "")
        ground_truth = item.get("ground_truth", "")
        response = item.get("response", "")
        context = item.get("context", "")

        # Citation validation
        has_citation = "[" in response and ".pdf]" in response
        if has_citation:
            citation_hits += 1

        # Grounding validation (terms overlap)
        gt_words = set(ground_truth.lower().split())
        resp_words = set(response.lower().split())
        overlap = len(gt_words.intersection(resp_words)) / max(len(gt_words), 1)
        is_grounded = overlap > 0.45
        if is_grounded:
            grounding_hits += 1

        # Check refusal / unsupported handling
        if "not" in ground_truth.lower() or "unavailable" in ground_truth.lower():
            if "unavailable" in response.lower() or "not specify" in response.lower() or "do not" in response.lower():
                refusal_hits += 1

        print(f"[{idx:02d}] Query: {query[:45]}...")
        print(f"     Citation Present: {'✓' if has_citation else '✗'} | Term Overlap: {overlap:.1%}")

    metrics = {
        "total_evaluated": total,
        "citation_coverage": f"{(citation_hits / total):.1%}",
        "grounding_alignment": f"{(grounding_hits / total):.1%}",
        "evaluation_dataset": str(EVAL_DATASET_PATH),
    }

    print("-" * 65)
    print("Evaluation Summary:")
    for k, v in metrics.items():
        print(f"  • {k.replace('_', ' ').capitalize()}: {v}")
    print("-" * 65)
    return metrics


if __name__ == "__main__":
    records = load_eval_dataset(EVAL_DATASET_PATH)
    evaluate_dataset(records)
