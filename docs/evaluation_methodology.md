# Evaluation methodology

## Metrics

| Metric | Question it answers | How |
|---|---|---|
| Context relevance | Did retrieval surface the right chunks? | Mean embedding similarity of query↔retrieved chunks |
| Answer relevance | Does the answer address the question? | Embedding similarity of query↔answer |
| Groundedness / faithfulness | Is each claim supported by retrieved context? | Fraction of answer sentences with a supporting context sentence |
| Judge score | LLM-as-judge groundedness verdict | Heuristic offline; OpenAI JSON verdict in prod |
| **Hallucination (ground truth)** | Does the answer contradict HURDAT2? | Parse the claimed category, compare to best-track truth |
| Latency / cost | Operational quality | Measured wall-clock; token-based cost |
| Reward | Optimization signal | `groundedness − hallucination_penalty` |

## Why a structured ground-truth check matters

Embedding-based groundedness and LLM judges both compare text to text. When a
wrong answer is *lexically* almost identical to the truth — "Category 3" vs
"Category 1" — they score it as grounded. The demo reproduces this exactly: both
the faithful and the hallucinating model score ~1.0 on groundedness, yet the
HURDAT2 check cleanly flags the hallucinating model (rate 1.00 vs 0.00). That
verifiable check is the core contribution.

## A/B testing

Two models (or two configurations) are compared on aligned per-question scores
with a paired bootstrap (95% CI) and a paired t-test. A change is reported as
*significant* only when both the CI excludes zero and p < 0.05. In the demo the
reward difference is +0.50 (95% CI [+0.13, +0.88], p≈0.03).

## Continuous improvement loop

1. Benchmark every model/prompt/retrieval change; log to MLflow.
2. Gate merges on the eval-regression CI job (hallucination rate must not
   regress above threshold).
3. Mine chosen/rejected **preference pairs** from scored answers.
4. Use the reward signal for best-of-N / preference-optimization experiments.
