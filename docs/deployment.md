# Deployment

Three things to put online: the **code** (GitHub), the **Weather Intelligence
page** (GitHub Pages — a clickable link for recruiters), and the **Streamlit
console** (Streamlit Community Cloud). All free. The FastAPI service is optional.

---

## 0. Verify locally first

```bash
unzip llm-eval-storm-platform.zip && cd llm-eval-storm-platform
python -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt && pip install -e .
make demo            # populates data/ ; prints the eval + model results
make test            # 17 passing
make weather         # builds dashboards/weather_intelligence.html
make dashboard       # opens the Streamlit console at localhost:8501
```

Open `dashboards/weather_intelligence.html` in a browser to confirm the map renders.

---

## 1. Push to GitHub

```bash
git init
git add .
git commit -m "Carolina Storm Intelligence: weather platform + LLM eval + landfall model"
git branch -M main
```

Create the repo (either way):

- **GitHub CLI:** `gh repo create carolina-storm-intelligence --public --source=. --push`
- **Web:** create an empty repo named `carolina-storm-intelligence`, then:
  ```bash
  git remote add origin https://github.com/<you>/carolina-storm-intelligence.git
  git push -u origin main
  ```

Generated artifacts (`data/warehouse.duckdb`, `data/vectorstore/`, `data/models/`,
`data/mlruns/`) are gitignored on purpose — the app rebuilds them.

CI runs automatically: the **ci** workflow (lint + 17 tests) and the
**eval-regression** gate. Add the badges from the blurb once they're green.

---

## 2. Weather Intelligence → GitHub Pages

A `pages.yml` workflow is already included. It builds the page and publishes it.

1. Push to `main` (done above).
2. On GitHub: **Settings → Pages → Build and deployment → Source = GitHub Actions**.
3. The **Deploy Weather Intelligence** workflow runs and gives you a URL like
   `https://<you>.github.io/carolina-storm-intelligence/`.

That URL is your headline portfolio link. (To re-publish after edits, just push —
the workflow rebuilds the page from the latest data.)

---

## 3. Streamlit console → Streamlit Community Cloud

The dashboards self-bootstrap (`dashboards/_bootstrap.py` builds the warehouse on
first load), so no data needs committing.

1. Go to <https://share.streamlit.io> and sign in with GitHub.
2. **New app** → pick the repo, branch `main`, main file `dashboards/Home.py`.
3. **Advanced settings → Python 3.11**. Deploy.

First load takes ~20–30 s while it builds the warehouse, then it's instant.
Streamlit Cloud installs `requirements.txt` automatically. You'll get a URL like
`https://<you>-carolina-storm-intelligence.streamlit.app`.

---

## 4. FastAPI service (optional)

Free hosts: Render or Railway.

- **Render:** New → Web Service → connect repo → Build `pip install -r requirements.txt && pip install -e .`
  → Start `uvicorn storm_eval.serving.api:app --host 0.0.0.0 --port $PORT`. Add a
  one-line build step `python scripts/build_index.py` so the vector store exists.
- **Docker (anywhere):** `docker compose -f docker/docker-compose.yml up`.

Swagger UI is at `/docs`; the live endpoints are `/query` and `/evaluate`.

---

## 5. Wire the links back into the repo

Put the two live URLs at the top of the README and in the GitHub **About** panel
(see `GITHUB.md`). A recruiter should reach a working demo in one click.

## Troubleshooting

- *Streamlit app shows "no warehouse":* the bootstrap import failed — confirm
  `pip install -e .` succeeded so `storm_eval` is importable.
- *Pages 404:* the Pages source must be **GitHub Actions**, not a branch.
- *FastAPI routes missing locally:* ensure a clean `pip install` (a mismatched
  Starlette breaks `include_router`); `requirements.txt` resolves a compatible one.
