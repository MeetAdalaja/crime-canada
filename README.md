# Crime Canada — Open Analysis & Dashboard (Ontario-focused)

An open project exploring **police-reported crime in Canada** (initial focus: **Ontario**) through
transparent research notebooks plus a web dashboard (frontend + API). The goal is to make
year-over-year trends, regional differences, and category-level patterns easy to explore — with
simple baseline forecasting for planning conversations.

[![Last commit](https://img.shields.io/github/last-commit/MeetAdalaja/crime-canada)](https://github.com/MeetAdalaja/crime-canada/commits/main)
[![Repo size](https://img.shields.io/github/repo-size/MeetAdalaja/crime-canada)](https://github.com/MeetAdalaja/crime-canada)
[![Open issues](https://img.shields.io/github/issues/MeetAdalaja/crime-canada)](https://github.com/MeetAdalaja/crime-canada/issues)
[![Website](https://img.shields.io/website?url=https%3A%2F%2Fcrime-ontario.vercel.app)](https://crime-ontario.vercel.app)
![Status](https://img.shields.io/badge/status-public_preview-blue)

---

## Live Demo

**▶️ https://crime-canada.vercel.app**

If you see a *404 Not Found* on the demo, confirm Vercel root is `frontend/` and SPA rewrites are enabled
(see **Deploy** section below).

---

## Table of Contents
- [Project Overview](#project-overview)
- [Tech Stack](#tech-stack)
- [Repository Structure](#repository-structure)
- [Quickstart](#quickstart)
  - [A) Explore the research notebooks](#a-explore-the-research-notebooks)
  - [B) Run the web app locally](#b-run-the-web-app-locally)
- [Data Sources](#data-sources)
- [How It Works](#how-it-works)
- [Deploy](#deploy)
- [Configuration](#configuration)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)
- [Citation](#citation)
- [Acknowledgements](#acknowledgements)

---

## Project Overview

- **Purpose:** Reproducible exploration of Canadian crime data with an Ontario-first lens,
  culminating in a shareable dashboard.
- **Current state:** Notebooks for EDA + baselines, with a dashboard frontend scaffold and
  planned API endpoints for clean data access.
- **Use cases:** Policy discussions, classroom demos, local trend exploration, lightweight forecasting experiments.

---

## Tech Stack

- **Research:** Python, Jupyter, pandas, NumPy, matplotlib/seaborn, scikit-learn
- **API (planned):** Python (FastAPI or Flask), uvicorn, pyarrow
- **Frontend:** React + Vite, TypeScript/JavaScript, Recharts/D3, Tailwind (planned)
- **Hosting:** Vercel (frontend), TBD for the API

---

## Repository Structure

```text
crime-canada/
├─ api/            # Backend service (WIP) – will expose endpoints for the dashboard
├─ frontend/       # Web UI (React/Vite, WIP) – charts, filters, tables
├─ research/       # Jupyter notebooks: EDA, feature prep, baseline modeling, notes
└─ .gitignore
```

> As development progresses, a `data/` directory (raw/curated) and `docs/` may be added.

---

## Quickstart

### A) Explore the research notebooks

1) **Clone**

```bash
git clone https://github.com/MeetAdalaja/crime-canada.git
cd crime-canada/research
```

2) **Create environment** (choose one)

**uv / pip**

```bash
python -m venv .venv && source .venv/bin/activate   # (Windows) .venv\Scriptsctivate
pip install -U pip wheel
pip install jupyter pandas numpy matplotlib seaborn scikit-learn pyarrow
```

**conda**

```bash
conda create -n crime-canada python=3.11 -y
conda activate crime-canada
conda install -y jupyter pandas numpy matplotlib seaborn scikit-learn pyarrow
```

3) **Launch notebooks**

```bash
jupyter lab
```
Open the notebooks in `research/` and run cells top-to-bottom.  
_Tip: when a `requirements.txt` or `environment.yml` is added, prefer those exact versions._

---

### B) Run the web app locally

**Frontend**

```bash
cd frontend
npm install          # or: pnpm install / yarn
npm run dev          # local dev server (Vite)
# npm run build && npm run preview  # production build preview
```

**API** (if/when available)

```bash
cd api
python -m venv .venv && source .venv/bin/activate   # (Windows) .venv\Scriptsctivate
pip install -U pip
# pip install -r requirements.txt
# uvicorn app.main:app --reload
```

---

## Data Sources

This project uses (or is designed to use) **open Canadian public-safety datasets**.
Add or substitute provincial/municipal sources as needed.

- **Toronto Police Service — Public Safety Data Portal** (open data, maps & dashboards)  
  https://data.torontopolice.on.ca/

- **Open Government Portal (Canada) — Police-reported crime indicators**  
  https://open.canada.ca/data/en/dataset/47466568-c38d-8bb9-26d9-331079dad727

- **Statistics Canada — Crime Severity Index (CSI) & incident tables**  
  Overview: https://www150.statcan.gc.ca/  
  Table example (incident-based crime statistics): https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=3510017701

> Always review each source’s methodology notes, data dictionaries, caveats, and release timelines.

---

## How It Works

1. **Research first**  
   Notebooks in `research/` perform data loading, cleaning (e.g., grouping by offence categories,
   year, geography), and exploratory visuals. Baseline models (classical regressors or time-series)
   can be prototyped here before promotion to the API.

2. **Data pipeline (planned)**  
   - Ingest raw CSVs/Parquet from public portals
   - Normalize fields (dates, offence codes, geography IDs)
   - Produce **curated tables** for the app (e.g., `facts_crime_by_year.csv`, `dim_geography.csv`)

3. **API (planned)**  
   - Read curated tables and provide endpoints such as:
     - `GET /regions` – list regions
     - `GET /metrics?region=...&from=...&to=...` – aggregated trends
     - `GET /forecast?region=...&offence=...` – simple forecast output

4. **Frontend**  
   - Filters: region, period, offence group
   - Charts: historical trends, YoY change, optional forecast overlay
   - Tables: selected crimes × years with totals/indices; CSV/PNG export

---

## Deploy

**Vercel (SPA) for `frontend/`:**

1. In Vercel → **Project Settings → General → Root Directory** → set to `frontend/`  
2. **Framework preset:** Vite (or “Other” if not listed)  
3. **Build command:** `npm run build`  
4. **Output directory:** `dist`  
5. Add a SPA rewrite to serve `index.html` for all routes. Either use the Vercel UI or create `vercel.json` at repo root:
   ```json
   {
     "rewrites": [{ "source": "/(.*)", "destination": "/index.html" }]
   }
   ```
6. Trigger a redeploy. The demo should be available at **https://crime-ontario.vercel.app**.

---

## Configuration

If environment variables are needed, create a local `.env` (not committed) with entries like:

```ini
# API
API_PORT=8000
API_HOST=127.0.0.1
# FRONTEND (Vite)
VITE_API_BASE=http://127.0.0.1:8000
```

Then read them in your API/frontend as appropriate.

---

## Roadmap

- [ ] Lock primary **data source(s)** and add dataset notes + direct download instructions
- [ ] Versioned **data artifacts** (e.g., `/data/curated/...`) and a light ETL script
- [ ] Minimal **API** with read-only endpoints for charts
- [ ] **Frontend** with filters, line/bar charts, and an export button (CSV/PNG)
- [ ] Optional **forecasting** overlay (with clear documentation of assumptions)
- [ ] CI checks (lint, notebook execution smoke test)
- [ ] Deployment: Vercel (frontend) + small host for API; add environment docs

---

## Contributing

Contributions, issues, and feature requests are welcome!

1. Open an issue describing the change.
2. For data additions, include links to **official sources** and a short data dictionary.
3. Keep notebooks deterministic (set seeds) and prefer small sample CSVs for tests.
4. Follow conventional commit messages where possible (e.g., `feat(api): add /regions`).

---

## License

_No license file has been added yet._  
If you plan to reuse code or data from this repo, please open an issue to discuss the intended license
(e.g., MIT/Apache-2.0) and data-source terms.

---

## Citation

If this work helps your research or product, please cite the repository:

```bibtex
@software{crime_canada_repo,
  author  = {Adalaja, Meet},
  title   = {Crime Canada — Open Analysis and Dashboard (Ontario-focused)},
  year    = {2025},
  url     = {https://github.com/MeetAdalaja/crime-canada}
}
```

---

## Acknowledgements

- The maintainers of open Canadian public-safety data portals and documentation.
- The open-source community for tools that make analysis and reproducibility possible.
