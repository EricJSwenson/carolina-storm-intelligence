# GitHub repo text

## Repo name
`carolina-storm-intelligence`

## Description (the "About" one-liner, ~120 chars)
> AI weather-intelligence platform for Atlantic storms: RAG assistant + landfall-intensity model, graded against NOAA HURDAT2 ground truth.

## Topics (paste into Settings → Topics)
```
machine-learning  llm  rag  llm-evaluation  mlops  data-engineering
databricks  pyspark  dbt  duckdb  mlflow  fastapi  streamlit
scikit-learn  retrieval-augmented-generation  noaa  weather  python
```

## About panel
- **Description:** the one-liner above
- **Website:** your GitHub Pages URL (the Weather Intelligence page)
- Check **Releases** off, pin the repo on your profile.

---

## Pinned-repo blurb (README hero / profile)

**Carolina Storm Intelligence** — an AI-powered weather platform over NOAA
Atlantic best-track data, with a trustworthy LLM-evaluation system underneath. A
RAG assistant answers questions from NOAA storm narratives and a gradient-boosted
model predicts landfall intensity — and **every answer and prediction is graded
against HURDAT2 ground truth**, so hallucinations are verifiable facts, not
another model's guess. Includes a medallion data pipeline (PySpark/Delta +
DuckDB), statistical A/B testing, an eval-regression CI gate, MLflow tracking, and
three dashboards. Runs end-to-end offline; `make demo` and `pytest` are green in CI.

🔗 **Live:** [Weather map](<pages-url>) · [Eval console](<streamlit-url>)

---

## Short social version (LinkedIn / "featured")

Built an AI weather-intelligence platform for Atlantic storms: a RAG assistant +
a landfall-intensity model, both graded against NOAA HURDAT2 ground truth. The
point — embedding and LLM-judge metrics rate a confidently wrong answer
("Category 3" vs the real "Category 1") as fully grounded; checking against
structured scientific data catches it. Python · Databricks/PySpark · dbt · MLflow
· scikit-learn · FastAPI · Streamlit, with A/B significance testing and a CI gate
that blocks hallucination regressions.

---

## Suggested commit message
```
Carolina Storm Intelligence: weather platform + LLM eval harness + landfall model
```

## README badges (add once CI is green; replace <you>)
```markdown
![CI](https://github.com/<you>/carolina-storm-intelligence/actions/workflows/ci.yml/badge.svg)
![Eval Gate](https://github.com/<you>/carolina-storm-intelligence/actions/workflows/eval-regression.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
```
