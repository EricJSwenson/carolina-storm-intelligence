# 🌀 Carolina Storm Intelligence Platform

An **AI-powered weather-intelligence platform** for Atlantic coastal storms —
with an integrated **LLM evaluation and model-monitoring system** underneath.

It does three things, and the whole stack runs offline with no API keys:

1. **Weather intelligence** — interactive hurricane tracks, landfall maps, an
   intensity history, and a searchable storm database over NOAA best-track data.
2. **A landfall-intensity model** — predicts a storm's NC landfall Saffir-Simpson
   category from its pre-landfall track (held-out, leakage-safe evaluation).
3. **A RAG assistant with a trustworthy evaluation harness** — answers questions
   from NOAA storm narratives and grades every answer against **HURDAT2 ground
   truth**, so hallucinations are *verifiable facts*, not another model's opinion.

**🔗 Live demo:** Weather map → `<github-pages-url>` · Eval console → `<streamlit-url>`
*(fill these in after deploying — see [docs/deployment.md](docs/deployment.md))*

> `make demo` runs the full pipeline (RAG eval **and** the landfall model);
> `pytest` is green in CI. The PySpark / dbt / MLflow / Databricks path carries
> the production story.

---

## Live data layer (Storm Center)

A server-side **Storm Center** page (Streamlit) adds live, location-aware NOAA data —
because static pages can't safely call these feeds (browser CORS), but the Python
app can:

- **Local forecast** (api.weather.gov), **tides** (NOAA CO-OPS), **buoy swell** (NDBC),
  for an auto-detected or user-entered location.
- **Active tropical cyclones** from the NHC, with the **official advisory bulletin**
  shown alongside a **landfall-category model estimate** — clearly labeled *not an
  official forecast*.
- A **RAG search bar** answering storm questions, checked against HURDAT2 ground truth.

Automated ingestion is wired via a scheduled GitHub Action
(`.github/workflows/live-data.yml`) that snapshots active storms every 6 hours. The
full roadmap (warehouse-backed pulls, advisory-cycle evaluation of the predictor) is
in [docs/live_data_plan.md](docs/live_data_plan.md). The platform's purpose stays
**evaluation against ground truth**; the live layer is additive.

## Three dashboards

| View | Audience | Shows |
|---|---|---|
| **Weather Intelligence** (`dashboards/weather_intelligence.html`, standalone) | recruiters / first impression | interactive Atlantic track map, landfall markers, intensity history, storm database, model card, assistant Q&A |
| **Model Evaluation** (Streamlit) | technical interviewers | RAG leaderboard, hallucination rate, groundedness, A/B significance, **landfall-model accuracy + confusion matrix** |
| **Experiment Tracking** (Streamlit) | ML engineers | config sweeps (chunk size, retrieval, embeddings, prompts) and metric movement across runs |
| **Storm Center** (Streamlit) | live demo | local forecast, tides, swell, active storms + NHC bulletin + model estimate, RAG search |

```bash
make weather      # build the Weather Intelligence page -> open the HTML
make dashboard    # Streamlit console: Model Evaluation + Experiment Tracking
```

---

## Why the evaluation is trustworthy

Most RAG portfolios grade answers with an LLM judge — which can't catch a
confidently-wrong fact. This platform pairs a **text corpus** (1.7M+ NOAA Storm
Events narratives + NWS forecast discussions for office KMHX, Morehead City, NC)
with independent **structured ground truth** (HURDAT2 best-track). The demo makes
the point concretely:

```
3) Benchmark models
   mock-grounded  groundedness=1.000  hallucination_rate=0.00 (on checked questions)
   mock-naive     groundedness=1.000  hallucination_rate=1.00 (on checked questions)

4) Statistical A/B test
   reward: mock-grounded - mock-naive = +0.500 (95% CI [+0.125, +0.875], p=0.0331, significant)

7) Train + evaluate the landfall-intensity model
   held-out: exact=0.810  within-1=1.000  macroF1=0.656  (test storms=58)
```

Embedding-groundedness rates the hallucinating model **1.0** — fooled because
"Category 3" reads almost identically to "Category 1". The HURDAT2 check catches
it cleanly. That contrast is the core idea.

---

## Architecture

```
Sources          Ingestion        Medallion (Delta / DuckDB)       Intelligence layer        Surfaces
Storm Events ─┐                   bronze  raw landed tables         RAG: retrieve→rerank      Weather Intelligence
HURDAT2       ├─► parsers ──────► silver  conformed tracks      ──► →generate→evaluate     ──► (HTML map)
NWS (KMHX)    │                          + narrative↔track join     Forecast: landfall        Streamlit console
NDBC buoys   ─┘                   gold    storm_truth + corpus       intensity model           FastAPI service
                                                                     Eval harness grades both  (/query /evaluate)
                                                          MLflow ◄── metrics · A/B · preference pairs · CI gate
```

The evaluation harness scores **both** model types — RAG answers and the
forecaster's category predictions — against HURDAT2. See
[`docs/architecture.md`](docs/architecture.md).

---

## Quickstart

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt && pip install -e .

make demo          # ingest → medallion → RAG eval → A/B → preference → landfall model
make weather       # build the Weather Intelligence HTML
make dashboard     # Streamlit: Model Evaluation + Experiment Tracking
make api           # FastAPI at :8000/docs
make test          # 17 unit + integration tests
```

No keys required — defaults are a deterministic hashing embedder, a numpy vector
store, two mock LLMs (one faithful, one that hallucinates), and a gradient-boosted
landfall classifier trained on synthetic best-tracks.

---

## The landfall-intensity model

A `HistGradientBoostingClassifier` predicts the NC landfall Saffir-Simpson
category from features knowable *before* landfall (pre-landfall wind/pressure,
24-hour intensification, latitude, forward speed). Evaluated with a **year-based
split** so no storm leaks between train and test. The bundled demo trains on
synthetic best-tracks (the real data is only three storms); point
`generate_dataset` at the full NCEI HURDAT2 download for production — the feature
builder is identical. Predictions flow into the same warehouse the LLM evaluator
uses, so the platform monitors the forecaster's accuracy alongside the RAG models.

---

## Repository layout

```
src/storm_eval/
  ingestion/     HURDAT2, Storm Events, NWS, NDBC parsers
  pipelines/     local.py (runnable medallion) + PySpark bronze/silver/gold
  rag/           embeddings · chunking · vectorstore · reranker · retriever · generator · pipeline
  evaluation/    metrics · judges · ground_truth · benchmark · ab_test
  forecasting/   dataset (synthetic + real) · features · model · evaluate   ← landfall model
  experiments/   config sweeps
  preference/    preference pairs + RLHF-style simulation
  serving/       FastAPI app
  tracking/      MLflow utils + model registry
dashboards/      weather_intelligence.html (standalone) + Streamlit Home/pages
notebooks/       Databricks production notebooks (01→04)
dbt/ sql/        marts + analytics queries
docker/ .github/ Dockerfiles, CI, nightly eval-regression gate
docs/            architecture · data_sources · evaluation_methodology · setup · interview_guide
data/samples/    offline sample data (Florence 2018, Dorian 2019, Irene 2011)
```

---

## Tech stack

Python · DuckDB / Delta Lake · PySpark · dbt · MLflow · scikit-learn · FastAPI ·
Streamlit · Plotly · NumPy / SciPy · Docker · GitHub Actions · OpenAI / Ollama /
Chroma / Pinecone (pluggable).

## Documentation

[Architecture](docs/architecture.md) ·
[Data sources](docs/data_sources.md) ·
[Evaluation methodology](docs/evaluation_methodology.md) ·
[Setup](docs/setup.md) ·
[Deployment](docs/deployment.md) ·
[Live data plan](docs/live_data_plan.md) ·
[Interview guide](docs/interview_guide.md)

## License

MIT — see [LICENSE](LICENSE). NOAA data is public domain; bundled sample
narratives and synthetic best-tracks were generated for this project.
