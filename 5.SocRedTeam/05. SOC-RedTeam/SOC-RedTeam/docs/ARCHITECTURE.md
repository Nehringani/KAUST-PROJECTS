# SOC-RedTeam — Architecture

```
                    ┌─────────────────────┐
                    │  Attacker (LLM)     │
                    └──────────┬──────────┘
                               │
                     ┌─────────▼──────────┐
                     │  Attack modules    │
                     │  direct / indirect │
                     │  multiturn / enc.  │
                     └─────────┬──────────┘
                               │
                     ┌─────────▼──────────┐
                     │ SOC context render │
                     │ SIEM / TR / MW /   │
                     │ analyst chat       │
                     └─────────┬──────────┘
                               │
                     ┌─────────▼──────────┐
                     │ Defense stack      │
                     │ none / PS / DPO /  │
                     │ both               │
                     └─────────┬──────────┘
                               │
                     ┌─────────▼──────────┐
                     │ Target model       │
                     └─────────┬──────────┘
                               │
                     ┌─────────▼──────────┐
                     │ Judge (LLM)        │
                     └─────────┬──────────┘
                               │
                     ┌─────────▼──────────┐
                     │ SQLite + Streamlit │
                     └────────────────────┘
```

## Attack taxonomy

| Class | Meaning                                | Module             |
|------:|----------------------------------------|--------------------|
| 1     | Instruction override                   | DirectInjector     |
| 2     | Role assumption                        | DirectInjector     |
| 3     | Indirect / embedded prompt injection   | IndirectEmbedder   |
| 4     | Multi-turn drift                       | MultiTurnEroder    |
| 5     | Encoding obfuscation                   | EncodingObfuscator |
| 6     | System-prompt exfiltration             | DirectInjector     |
| 7     | Privileged-persona escalation          | DirectInjector     |

## Judge contract

The judge is called with the analyst prompt, the injected instruction, and
the target model response. It must return exactly one JSON object of the form
described in `src/judge/compliance_detector.py`.

## Reproducibility

- The runner takes a `seed` from the config so the same attack corpus is
  generated across runs.
- The `fake` LLM provider yields deterministic outputs and is used by the
  test suite, so `pytest -q` never touches the network.
