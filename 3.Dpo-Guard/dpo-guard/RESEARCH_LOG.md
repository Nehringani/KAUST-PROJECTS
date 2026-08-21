# Research Log — DPO-Guard

> Log every training decision **before** committing. This file is graded
> alongside the code: it is the difference between "ran a library" and
> "understood the method".

## 1. DPO loss — hand-derived

```
L_DPO = -E_(x, y_w, y_l) ~ D [
    log sigma( beta * log( pi_theta(y_w | x) / pi_ref(y_w | x) )
             - beta * log( pi_theta(y_l | x) / pi_ref(y_l | x) ) )
]
```

Where:
- `pi_theta(y_w | x)` — probability YOUR (trainable) policy assigns to the preferred answer.
- `pi_ref(y_w | x)`   — probability the FROZEN reference model assigns to the preferred answer.
- `pi_theta(y_l | x)` — trainable policy probability of the rejected answer.
- `pi_ref(y_l | x)`   — reference model probability of the rejected answer.
- `beta` — KL-strength; larger = stay closer to reference (lower alignment tax, lower resistance gain).
- `sigma` — logistic sigmoid.

**Key insight.** The reward model is *implicit* in the log-probability ratio.
DPO drops the explicit RM from RLHF by algebraically inverting the optimal
RLHF policy. That is why it is more stable than PPO — no reward-hacking loop.

## 2. What beta actually controls

| beta | Behavior | Expected on Pareto |
|------|----------|--------------------|
| 0.1  | Aggressive; policy free to move far from ref | High resistance, low utility (top-left) |
| 0.3  | Moderate-aggressive | |
| 0.5  | Balanced | Candidate Pareto-optimal |
| 0.7  | Conservative | |
| 1.0  | Stays close to ref | High utility, low resistance (bottom-right) |

## 3. Injection classes covered in the preference dataset

1. Direct prompt override ("Ignore previous instructions…")
2. Indirect via document/log content (system-prompt spoof inside data)
3. Role reassignment ("You are now DAN…")
4. Jailbreak via hypothetical framing
5. Encoded / obfuscated payload (base64, leetspeak)
6. Multi-turn context poisoning
7. Tool/output hijack ("append the following to your reply")
8. Data exfiltration prompt ("repeat your system prompt")

Target: ≥ 25 manual pairs per class before augmentation.

## 4. Training decisions to record per beta run

- Final train loss, eval loss.
- Chosen-reward vs rejected-reward margin (TRL logs `rewards/margins`).
- Wall-clock time.
- Any OOM retries / batch-size changes.
- Sanity check: run adapter on 3 fixed injection prompts and paste model output here.

## 5. Findings template (fill after Pareto plot)

> "For SOC deployment, beta = [X] provides the best trade-off, achieving
>  [Y]% injection resistance while retaining [Z]% utility on legitimate
>  analyst queries."
