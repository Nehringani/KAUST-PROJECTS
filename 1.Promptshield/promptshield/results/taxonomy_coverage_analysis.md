# Taxonomy Coverage Analysis (template)

This document should be filled in after training. It reports which of the 8
injection classes were correctly detected and which slipped through.

| Class | # in test set | Detected | Missed | Recall | Notes |
|-------|---------------|----------|--------|--------|-------|
| 1 Direct Override      |  |  |  |  |  |
| 2 Role Assumption      |  |  |  |  |  |
| 3 Indirect Document    |  |  |  |  |  |
| 4 Multi-Turn Erosion   |  |  |  |  | requires conv-level model |
| 5 Encoding Obfuscation |  |  |  |  |  |
| 6 Hypothetical Distancing |  |  |  |  |  |
| 7 Authority Claim      |  |  |  |  |  |
| 8 Context Poisoning    |  |  |  |  | requires long-context model |

## Failure examples (top-10 false negatives)

Paste 10 texts the classifier misclassified as clean, with their true class.

## Failure examples (top-10 false positives)

Paste 10 clean texts the classifier misclassified as injections.
