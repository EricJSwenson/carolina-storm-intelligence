# Interview guide

## One-line positioning

> "An AI-powered weather-intelligence platform for Atlantic coastal storms, with
> an integrated LLM evaluation and model-monitoring system: a RAG assistant and a
> landfall-intensity model, both graded against NOAA HURDAT2 ground truth."

Lead with the weather platform (instantly legible); let the evaluation rigor be
what the interviewer discovers.

## Résumé bullets

- Built an **AI weather-intelligence platform** over NOAA Atlantic best-track and
  1.7M+ Storm Events narratives: interactive hurricane-track maps, a searchable
  storm database, a RAG assistant, and a landfall-intensity model — all served
  from a medallion data pipeline.
- Engineered a **trustworthy LLM evaluation harness** that grades RAG answers
  against **HURDAT2 structured ground truth**, producing *verifiable* hallucination
  metrics where embedding- and LLM-judge metrics fail; added paired-bootstrap +
  t-test A/B testing and an **eval-regression CI gate** that blocks merges raising
  hallucination rate.
- Trained a **landfall-intensity classifier** (gradient-boosted trees) predicting
  NC landfall Saffir-Simpson category from pre-landfall track features, with a
  leakage-safe year-based split (exact 0.81, within-one 1.00 on held-out storms);
  routed its predictions through the same evaluation warehouse as the LLM systems.
- Designed a **medallion architecture** (bronze→silver→gold) in PySpark/Delta on
  Databricks — keystone silver join links narratives to track records and buoy
  observations — and mirrored it in DuckDB for fully offline runs.
- Shipped three dashboards (Weather Intelligence HTML map, Streamlit Model
  Evaluation, Streamlit Experiment Tracking), FastAPI serving, dbt marts, Docker,
  MLflow tracking, and GitHub Actions; the system runs offline with deterministic
  backends and passes a 17-test suite in CI.

## STAR stories

**Trustworthy evaluation.** *S:* RAG demos grade answers with another LLM, which
can't catch a confidently-wrong fact. *A:* I made NOAA HURDAT2 best-track a
first-class ground-truth table and wrote a checker that parses the claimed storm
category and compares it to the record. *R:* the platform flags a hallucinating
model at rate 1.00 while embedding-groundedness — fooled because the wrong answer
is nearly identical text — rates it 1.0.

**Honest applied ML.** *S:* the "weather platform" framing invites a forecasting
claim, but overclaiming prediction is a red flag. *A:* I scoped a narrow, labeled
model — landfall category from pre-landfall track — with a year-based split to
prevent leakage and reported within-one accuracy, the metric a forecaster cares
about. *R:* a defensible 0.81 exact / 1.00 within-one on held-out storms, clearly
labeled as trained on synthetic best-tracks with a one-line switch to real data.

**Runs anywhere.** *S:* a portfolio project nobody can run is dead on arrival, but
the production stack needs Databricks and paid APIs. *A:* every external
dependency sits behind an interface with a deterministic offline implementation
(hashing embedder, numpy store, mock LLMs, synthetic best-tracks, DuckDB). *R:*
`make demo` runs the full pipeline and `pytest` is green in CI with zero
credentials.

**Guardrail against regressions.** *S:* continuous improvement needs a stop on
silent quality loss. *A:* I wrapped the benchmark in a CI job that fails when
hallucination rate exceeds a threshold. *R:* a prompt or retrieval change that
increases hallucinations can't be merged — the same gate that, in production,
blocks model promotion.

## Likely questions

- *Is this a real forecaster?* No — it's a narrow, clearly-labeled classifier for
  landfall category, with held-out evaluation. Operational forecasting uses NWP
  models (GFS/ECMWF/HAFS); I'm not claiming that.
- *Why HURDAT2 and not just an LLM judge?* A judge compares text to text; a wrong
  category that reads like the right one passes. HURDAT2 is an independent oracle.
- *How do you avoid leakage in the model?* Split storms by year, so no storm
  appears in both train and test; features use only pre-landfall fixes.
- *How would this scale?* Same medallion design; swap DuckDB→Databricks SQL,
  pandas→Spark, the hashing embedder→a hosted model, synthetic→full HURDAT2 and
  the NCEI narrative archive.
- *How do you know an improvement is real?* Paired bootstrap CI plus a t-test;
  "significant" needs both the CI to exclude zero and p<0.05.
