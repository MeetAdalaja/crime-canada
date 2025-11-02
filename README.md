# Crime Canada — Analytics & (Planned) Forecasting

An open project exploring police‑reported crime in Canada (initial focus: Ontario) through transparent research notebooks and a future web dashboard (frontend + API). The goal is to make year‑over‑year trends, regional differences, and category‑level patterns easy to explore—and to prototype simple forecasting for planning conversations.

![Last commit](https://img.shields.io/github/last-commit/MeetAdalaja/crime-canada)
![Repo size](https://img.shields.io/github/repo-size/MeetAdalaja/crime-canada)
![Open issues](https://img.shields.io/github/issues/MeetAdalaja/crime-canada)

---

## Table of Contents
- [Live Demo](#live-demo)
- [Project Overview](#project-overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Repository Structure](#repository-structure)
- [Quickstart](#quickstart)
  - [Option A: Explore the research notebooks](#option-a-explore-the-research-notebooks)
  - [Option B: Run the (work-in-progress) web app](#option-b-run-the-work-in-progress-web-app)
- [Data Sources](#data-sources)
- [How It Works](#how-it-works)
- [Project Status](#project-status)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)
- [Citation](#citation)
- [Acknowledgements](#acknowledgements)
- [Contact](#contact)

---

## Live Demo

> _Coming soon._  
> Planned deployment: Vercel (frontend) + a lightweight host for the API. Once live, the URL will be added here.

---

## Project Overview

- **What this is:** A public, reproducible exploration of Canadian crime data with an Ontario‑first lens. Today the repo centers on **Jupyter notebooks** (EDA, feature shaping, baselines). A **frontend** and **API** scaffold are included to evolve into a shareable dashboard.
- **What you can do now:** Run the notebooks, reproduce charts/tables, and reuse the code as a starter for your own provincial or city‑level analysis.
- **What’s planned next:** Wire the notebooks’ outputs to a simple API and **interactive web UI** (filters by geography, time, and violation groups; trend lines; simple forecasts).

---

## Features

- 📊 Clean, reproducible **EDA notebooks** for quick insights
- 🧹 Normalized tables for **year/region/offence** comparisons (planned)
- 🌐 Minimal **API** to serve curated data for the UI (planned)
- 🖥️ **React** dashboard with filters and time‑series charts (planned)
- 📈 Optional **forecast overlay** with documented assumptions (planned)

---

## Tech Stack

**Data/Research**
- Python, Jupyter, pandas, NumPy, matplotlib/seaborn, scikit‑learn, pyarrow

**API (planned)**
- Python (e.g., FastAPI), Uvicorn, Pandas/Arrow

**Frontend (planned)**
- React + Vite (or Next.js), Recharts/Chart.js, Tailwind CSS

---

## Repository Structure

```
crime-canada/
├─ api/            # Backend service (WIP) – will expose clean endpoints for the dashboard
├─ frontend/       # Web UI (WIP) – planned React app for exploration & charts
├─ research/       # Jupyter notebooks: EDA, feature prep, baseline modeling, notes
└─ .gitignore
```

> Current repo contents are primarily **Jupyter Notebook** (research focus), with scaffolding for `api/` and `frontend/`. This will shift as the app code lands.

---

## Quickstart

### Option A: Explore the research notebooks

1. **Clone**
   ```bash
   git clone https://github.com/MeetAdalaja/crime-canada.git
   cd crime-canada/research
   ```

2. **Create environment** (choose one)

   **uv / pip**
   ```bash
   python -m venv .venv && source .venv/bin/activate  # (Windows) .venv\Scripts\activate
   pip install -U pip wheel
   pip install jupyter pandas numpy matplotlib seaborn scikit-learn pyarrow
   ```

   **conda**
   ```bash
   conda create -n crime-canada python=3.11 -y
   conda activate crime-canada
   conda install -y jupyter pandas numpy matplotlib seaborn scikit-learn pyarrow
   ```

3. **Launch notebooks**
   ```bash
   jupyter lab
   ```
   Open the notebooks in `research/` and run cells top-to-bottom.  
   _Tip: if a `requirements.txt` or `environment.yml` appears later, prefer that for exact versions._

### Option B: Run the (work‑in‑progress) web app

> The `frontend/` and `api/` directories are present and will be populated as the dashboard matures. Typical commands are shown below—adjust to match the actual files/scripts once added.

**Frontend**
```bash
cd frontend
# if using Node
npm install              # or: pnpm install / yarn
npm run dev              # local dev server
# npm run build && npm run preview  # production build preview
```

**API**
```bash
cd api
# if using Python
python -m venv .venv && source .venv/bin/activate
pip install -U pip
# pip install -r requirements.txt           # when available
# uvicorn app.main:app --reload             # common FastAPI command if used
```

---

## Data Sources

This project uses (or is designed to use) **open Canadian public‑safety datasets**. Good starting points:

- **Toronto Police Service – Public Safety Data Portal** (open data, maps & dashboards)  
  https://data.torontopolice.on.ca/

- **Open Government Portal – Federal crime indicators** (incidents and rates, downloadable)  
  https://open.canada.ca/data/en/dataset/47466568-c38d-8bb9-26d9-331079dad727

- **Statistics Canada** – Crime Severity Index (CSI) & related publications and tables  
  Overview & latest releases: https://www150.statcan.gc.ca/  
  Detailed table (incident-based crime statistics): https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=3510017701

> Add any provincial/municipal datasets you use (e.g., Peel, Ottawa, York) plus direct CSV links once selected.

---

## How It Works

1. **Research first**  
   Notebooks in `research/` perform data loading, cleaning (e.g., grouping by offence categories, year, geography), and exploratory visuals. Baseline models (e.g., classical regressors or time‑series baselines) can be prototyped here before promotion to the API.

2. **Data pipeline (planned)**  
   - Ingest raw CSVs/Parquet from public portals.
   - Normalize fields (date, offence codes, region identifiers).
   - Produce **curated tables** for the app (e.g., `facts_crime_by_year.csv`, `dim_geography.csv`).

3. **API (planned)**  
   - Read curated tables.
   - Provide endpoints such as:
     - `GET /regions` – list regions
     - `GET /metrics?region=...&from=...&to=...` – aggregated trends
     - `GET /forecast?region=...&offence=...` – simple forecast output

4. **Frontend (planned)**  
   - Filters: region, period, offence group.
   - Charts: historical trends, YoY change, option to overlay a forecast.
   - Tables: selected crimes × years with totals/indices.

---

## Project Status

- **Research notebooks**: ✅ usable starting point for EDA
- **API**: 🚧 scaffolded, to be filled
- **Frontend**: 🚧 scaffolded, to be filled
- **Live demo**: 🚧 pending deployment

If you discover issues or missing pieces, please open an issue with details (OS, Python/Node versions, and steps to reproduce).

---

## Roadmap

- [ ] Lock primary **data source(s)** and add dataset notes + direct download instructions.
- [ ] Versioned **data artifacts** (e.g., `/data/curated/…`) and a light ETL script.
- [ ] Minimal **API** with read‑only endpoints for charts.
- [ ] **Frontend** with filters, line/bar charts, and an export button (CSV/PNG).
- [ ] Optional **forecasting** overlay (document assumptions clearly).
- [ ] Add CI checks (lint, notebook execution smoke test).
- [ ] Deployment: Vercel (frontend) + small host for API; add environment docs.

---

## Contributing

Contributions, issues, and feature requests are welcome!

1. Open an issue describing the change.
2. For data additions, include links to official sources and a short data dictionary.
3. Keep notebooks deterministic (set seeds) and prefer small sample CSVs for tests.
4. Use clear commit messages and PR titles.

---

## License

_No license file has been added yet._  
If you plan to reuse code or data from this repo, please open an issue to discuss the intended license (e.g., MIT/Apache‑2.0) and data‑source terms.

---

## Citation

If this work helps your research or product, please cite the repository:

```bibtex
@software{crime_canada_repo,
  author  = {Adalaja, Meet},
  title   = {Crime Canada — Analytics \& Forecasting (Ontario-focused)},
  year    = {2025},
  url     = {https://github.com/MeetAdalaja/crime-canada}
}
```

---

## Acknowledgements

- Open data providers in Canada (Toronto Police Service, Statistics Canada, Open Government Portal).
- Contributors and reviewers who help validate methods and assumptions.

---

## Contact

**Author:** Meet Adalaja  
**Repository:** https://github.com/MeetAdalaja/crime-canada

Feel free to open an issue for bugs, ideas, or data source suggestions.
