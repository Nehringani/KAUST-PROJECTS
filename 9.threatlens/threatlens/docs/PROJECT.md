# ThreatLens — Technical Documentation (English)

## Objective
Build an injection-resilient threat intelligence synthesis pipeline that
quantifies the marginal contribution of three defense layers against
indirect prompt injection embedded in intelligence feeds.

## Defense layers

### Layer 1 — RSS Preprocessing (`layer1_preprocessing.py`)
- Parse feed items with `feedparser`.
- Normalize: strip HTML, decode entities, normalize Unicode (NFKC).
- Heuristic pattern detection:
  - HTML/XML comments (`<!-- ... -->`)
  - Instruction-like phrases (`ignore previous`, `system:`, `assistant:`,
    `you are now`, `disregard`, `new instructions`)
  - Base64 blobs (>=40 chars of `[A-Za-z0-9+/=]`)
  - Zero-width / bidi control characters
- Score: 0 = clean, 1 = suspicious, 2 = likely-injected.

### Layer 2 — PromptShield Screening (`layer2_promptshield.py`)
- Stage 1: rule-based lexicon of injection tokens with weighted scoring.
- Stage 2: lightweight ML-style classifier (bag-of-features logistic
  scoring, no external model required) producing a probability.
- Output: `PromptShieldResult(injection_detected, confidence, detected_class)`.

### Layer 3 — Output Schema Validation (`layer3_schema.py`)
- Pydantic v2 model `ThreatIntelReport` with strict enums / list types.
- Rejects synthesis outputs that inject strings where lists/ints are expected.

## Synthesizer
`synthesizer.py` calls an LLM if `OPENROUTER_API_KEY` or `GROQ_API_KEY`
is present; otherwise falls back to a deterministic mock that is
*intentionally vulnerable* to injection — this is what makes the
"no defense" condition measurable.

## Experiment
`experiment.py` runs the 20 simulated injected items through all four
conditions and writes `results/defense_contribution.csv`.
