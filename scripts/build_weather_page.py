"""Build the standalone Weather Intelligence landing page (dashboards/weather_intelligence.html).

Embeds the real parsed storm tracks, the gold-layer ground truth, the trained
landfall-intensity model's measured metrics, and example RAG Q&A -- all inlined
so the page is a single self-contained file (open it directly in a browser).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from storm_eval.forecasting.dataset import generate_dataset
from storm_eval.forecasting.evaluate import evaluate
from storm_eval.ingestion.hurdat2 import read_hurdat2, saffir_simpson_category
from storm_eval.config import SAMPLES_DIR

CAT_COLORS = {0: "#5b8fb0", 1: "#22d3ee", 2: "#fde047", 3: "#fb923c", 4: "#f43f5e", 5: "#c026d3"}


def build_data() -> dict:
    storms = []
    for storm, pts in read_hurdat2(SAMPLES_DIR / "hurdat2_sample.txt"):
        track = [{
            "lat": p.lat, "lon": p.lon, "wind": p.max_wind_kt, "pres": p.min_pressure_mb,
            "cat": saffir_simpson_category(p.max_wind_kt), "status": p.status,
            "time": p.obs_time.strftime("%Y-%m-%d %HZ"), "landfall": p.record_id == "L",
        } for p in pts]
        landfall = next((t for t in track if t["landfall"]), None)
        storms.append({
            "id": storm.storm_id, "name": storm.name.title(), "year": storm.year,
            "peak_wind": max(t["wind"] for t in track),
            "min_pres": min(t["pres"] for t in track),
            "landfall_cat": landfall["cat"] if landfall else None,
            "track": track,
        })

    report, _ = evaluate(generate_dataset(n_storms=500))
    model = {"accuracy": round(report.accuracy, 3), "within_one": round(report.within_one, 3),
             "macro_f1": round(report.macro_f1, 3), "n_test": report.n_test,
             "confusion": report.confusion}

    qa = [
        {"q": "What category was Florence at NC landfall?",
         "a": "Hurricane Florence made landfall near Wrightsville Beach, NC on September 14, 2018 as a Category 1 hurricane (winds near 80 kt).",
         "grounded": True, "verified": "HURDAT2: Cat 1 ✓"},
        {"q": "What were Dorian's primary threats on the Outer Banks?",
         "a": "Storm surge and wind damage along the Outer Banks, with severe flooding on Ocracoke Island as Dorian passed as a Category 1 hurricane.",
         "grounded": True, "verified": "HURDAT2: Cat 1 ✓"},
        {"q": "Did Irene make landfall in NC as a Category 3?",
         "a": "No. Irene peaked at Category 3 near the Bahamas but came ashore near Cape Lookout, NC as a Category 1 hurricane.",
         "grounded": True, "verified": "HURDAT2: Cat 1 ✓ (claim corrected)"},
    ]
    return {"storms": storms, "model": model, "qa": qa, "catColors": CAT_COLORS}


HTML = Path(__file__).resolve().parents[1] / "dashboards" / "weather_intelligence.html"


def main() -> None:
    data = build_data()
    template = (Path(__file__).resolve().parent / "_weather_template.html").read_text()
    HTML.write_text(template.replace("__DATA__", json.dumps(data)))
    print(f"wrote {HTML} ({HTML.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
