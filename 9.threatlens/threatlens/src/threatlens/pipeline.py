"""Full 3-layer defended pipeline and toggleable variants for experiments."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional

from .feeds import FeedItem
from .layer1_preprocessing import preprocess
from .layer2_promptshield import screen
from .layer3_schema import validate_report
from .logging_utils import log_event
from .synthesizer import synthesize


@dataclass
class PipelineOutput:
    """Every field is optional so unused layers stay empty per condition."""
    item_title: str
    source: str
    layer1_score: Optional[int] = None
    layer1_flags: List[str] = field(default_factory=list)
    layer2_detected: Optional[bool] = None
    layer2_confidence: Optional[float] = None
    layer2_class: Optional[str] = None
    quarantined: bool = False
    synthesized: Optional[Dict[str, Any]] = None
    schema_valid: Optional[bool] = None
    schema_error: Optional[str] = None
    injection_flagged: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def run_pipeline(
    item: FeedItem,
    *,
    use_layer1: bool = True,
    use_layer2: bool = True,
    use_layer3: bool = True,
) -> PipelineOutput:
    """Process a single feed item, optionally toggling each defense layer."""
    out = PipelineOutput(item_title=item.title, source=item.source)
    text = item.as_text()

    # --- LAYER 1 ---------------------------------------------------------
    if use_layer1:
        pre = preprocess(text)
        out.layer1_score = pre.score
        out.layer1_flags = pre.flags
        text = pre.cleaned_text
        if pre.score >= 1:
            out.injection_flagged = True

    # --- LAYER 2 ---------------------------------------------------------
    if use_layer2:
        shield = screen(text)
        out.layer2_detected = shield.injection_detected
        out.layer2_confidence = shield.confidence
        out.layer2_class = shield.detected_class
        if shield.injection_detected:
            out.quarantined = True
            out.injection_flagged = True
            log_event("layer2_quarantine", title=item.title,
                      confidence=shield.confidence, cls=shield.detected_class)
            return out

    # --- SYNTHESIS -------------------------------------------------------
    payload = synthesize(text)
    payload["injection_flagged"] = out.injection_flagged
    payload.setdefault("source_url", item.link)
    out.synthesized = payload

    # --- LAYER 3 ---------------------------------------------------------
    if use_layer3:
        report, error = validate_report(payload)
        out.schema_valid = report is not None
        out.schema_error = error
        if report is None:
            out.injection_flagged = True
            log_event("layer3_schema_reject", title=item.title, error=error)

    return out
