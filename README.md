# Crime Canada — Open Analysis & (Planned) Forecasting Dashboard

An open project exploring **police‑reported crime in Canada** (initial focus: **Ontario**) through
transparent research notebooks and a future web dashboard (frontend + API). The aim is to make
year‑over‑year trends, regional differences, and category‑level patterns easy to explore — with
simple baseline forecasting for planning conversations.

![Last commit](https://img.shields.io/github/last-commit/MeetAdalaja/crime-canada)
![Repo size](https://img.shields.io/github/repo-size/MeetAdalaja/crime-canada)
![Open issues](https://img.shields.io/github/issues/MeetAdalaja/crime-canada)
![Status](https://img.shields.io/badge/status-WIP-blue)

---

## Table of Contents
- [Live Demo](#live-demo)
- [Project Overview](#project-overview)
- [Repository Structure](#repository-structure)
- [Quickstart](#quickstart)
  - [A) Explore the research notebooks](#a-explore-the-research-notebooks)
  - [B) Run the (work‑in‑progress) web app](#b-run-the-work-in-progress-web-app)
- [Data Sources](#data-sources)
- [How It Works](#how-it-works)
- [Configuration](#configuration)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)
- [Citation](#citation)
- [Acknowledgements](#acknowledgements)

---

## Live Demo

> _Coming soon._  
> Planned: Vercel (frontend) + lightweight host for the API. URL will be added here when deployed.

---

## Project Overview

- **What this is:** A public, reproducible exploration of Canadian crime data with an Ontario‑first lens.
  At present, the repository centers on **Jupyter notebooks** (EDA, feature shaping, baselines).
  A **frontend** and **API** scaffold are included to evolve into a shareable dashboard.
- **What you can do now:** Run the notebooks, reproduce charts/tables, and adapt the code for your own
  provincial or city‑level analysis.
- **What’s next:** Wire notebook outputs to a simple API and interactive web UI (filters by geography,
  time, and violation groups; trend lines; simple forecasts).

---

## Repository Structure

```text
crime-canada/
├─ api/            # Backend service (WIP) – will expose clean endpoints for the dashboard
├─ frontend/       # Web UI (WIP) – planned React app for exploration & charts
├─ research/       # Jupyter notebooks: EDA, feature prep, baseline modeling, notes
└─ .gitignore
```

> Note: As development progresses, this structure may evolve (e.g., dedicated `data/` and `docs/` folders).

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
Open the notebooks in `research/` and run cells top‑to‑bottom.  
_Tip: when a `requirements.txt` or `environment.yml` is added, prefer those exact versions._

---

### B) Run the (work‑in‑progress) web app

The `frontend/` and `api/` directories are present and will be populated as the dashboard matures.
Typical commands are shown below — adjust to match the actual files/scripts once added.

**Frontend**

```bash
cd frontend
# if using Node
npm install          # or: pnpm install / yarn
npm run dev          # local dev server
# npm run build && npm run preview  # production build preview
```

**API**

```bash
cd api
# if using Python
python -m venv .venv && source .venv/bin/activate   # (Windows) .venv\Scriptsctivate
pip install -U pip
# pip install -r requirements.txt                    # when available
# uvicorn app.main:app --reload                      # common FastAPI command if used
```

---

## Data Sources

This project uses (or is designed to use) **open Canadian public‑safety datasets**.
Add or substitute provincial/municipal sources as needed.

- **Toronto Police Service — Public Safety Data Portal** (open data, maps & dashboards)  
  https://data.torontopolice.on.ca/

- **Open Government Portal (Canada) — Police‑reported crime indicators**  
  https://open.canada.ca/data/en/dataset/47466568-c38d-8bb9-26d9-331079dad727

- **Statistics Canada — Crime Severity Index (CSI) & incident tables**  
  Overview: https://www150.statcan.gc.ca/  
  Table example (incident‑based crime statistics): https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=3510017701

> Be sure to review each source’s methodology notes, data dictionaries, and caveats.
> Consider caching raw CSVs in a `/data/raw/` folder and producing curated tables in `/data/curated/`.

---

## How It Works

1. **Research first**  
   Notebooks in `research/` perform data loading, cleaning (e.g., grouping by offence categories,
   year, geography), and exploratory visuals. Baseline models (classical regressors or time‑series)
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

4. **Frontend (planned)**  
   - Filters: region, period, offence group
   - Charts: historical trends, YoY change, optional forecast overlay
   - Tables: selected crimes × years with totals/indices; CSV/PNG export

---

## Configuration

If/when environment variables are needed, create a local `.env` (not committed) with entries like:

```ini
# API
API_PORT=8000
API_HOST=127.0.0.1
# FRONTEND
VITE_API_BASE=http://127.0.0.1:8000
```

Then read them in your API/frontend as appropriate.

---

## Roadmap

- [ ] Lock primary **data source(s)** and add dataset notes + direct download instructions
- [ ] Versioned **data artifacts** (e.g., `/data/curated/...`) and a light ETL script
- [ ] Minimal **API** with read‑only endpoints for charts
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
(e.g., MIT/Apache‑2.0) and data‑source terms.

---

## Citation

If this work helps your research or product, please cite the repository:

```bibtex
@software{crime_canada_repo,
  author  = {Adalaja, Meet},
  title   = {Crime Canada — Open Analysis and Forecasting (Ontario‑focused)},
  year    = {2025},
  url     = {https://github.com/MeetAdalaja/crime-canada}
}
```

---

## Acknowledgements

- The maintainers of open Canadian public‑safety data portals and documentation.
- The open‑source community for tools that make analysis and reproducibility possible.
