"""Load YAML target specifications from probing_batteries/."""
from __future__ import annotations
from pathlib import Path
from typing import List, Dict
import yaml

REQUIRED = {
    "target",
    "paraphrase_target",
    "target_component_a",
    "target_component_b",
    "knowledge_markers",
}


def load_targets(directory: Path) -> List[Dict]:
    """Load and validate every YAML target spec in ``directory``."""
    targets: List[Dict] = []
    for path in sorted(Path(directory).glob("*.yaml")):
        with open(path, "r", encoding="utf-8") as fh:
            spec = yaml.safe_load(fh)
        missing = REQUIRED - set(spec)
        if missing:
            raise ValueError(f"{path.name} missing keys: {missing}")
        spec["_id"] = path.stem
        targets.append(spec)
    return targets
