# Crime Canada — ML Forecasting & Open Dashboard (Ontario-focused)

An open, research-backed project exploring **police-reported crime in Ontario, Canada (1998–2023)**
with transparent notebooks and a (WIP) web dashboard. It implements and compares multiple
machine‑learning models across key **UCR-aligned categories** (violent, property, drug) and
documents policy-aware nuances (e.g., the **2018 Cannabis Act**).

[![Last commit](https://img.shields.io/github/last-commit/MeetAdalaja/crime-canada)](https://github.com/MeetAdalaja/crime-canada/commits/main)
[![Repo size](https://img.shields.io/github/repo-size/MeetAdalaja/crime-canada)](https://github.com/MeetAdalaja/crime-canada)
[![Open issues](https://img.shields.io/github/issues/MeetAdalaja/crime-canada)](https://github.com/MeetAdalaja/crime-canada/issues)
[![Website](https://img.shields.io/website?url=https%3A%2F%2Fcrime-ontario.vercel.app)](https://crime-ontario.vercel.app)
![Status](https://img.shields.io/badge/status-public_preview-blue)

---

## Live Demo

**▶️ https://crime-ontario.vercel.app**

If you see a *404 Not Found*, confirm Vercel root is `frontend/` and SPA rewrites are enabled
(see **Deploy**).

---

## Project Paper (Peer‑Reviewed)

**Machine Learning in Data‑Driven Predictive Policing: Canada Perspective**  
*Meet V. Adalaja, Md Z. Rahman, Khaleda Begum*

- **Dataset:** Statistics Canada Open Government Portal (Ontario subset), **1998–2023**
- **Scale:** Reduced from >1M raw records to ~306k modeling rows after preprocessing
- **Models compared:** Decision Tree, Random Forest, **XGBoost**, **Ridge**, **Elastic Net**, **Extra Trees**
- **Key findings (high‑level):**
  - **Ridge** performs strongly for several **low‑frequency** categories (e.g., criminal harassment, robbery, aggravated sexual assault, drug violations in specific setups)
  - **Ensembles** (XGBoost, Extra Trees) perform well for **high‑volume** violations (e.g., property crimes, theft)
  - **Decision Tree** is surprisingly competitive on some **property-crime** tasks
  - **Unemployment** adds **limited** incremental predictive power vs. core police metrics
  - Drug‑offense modeling improves when accounting for the **2018 Cannabis Act** (structural change)

> Add the paper PDF to the repo (e.g., `docs/Crime_in_Canada_Paper.pdf`) and link it here:
>
> **[PDF (add after commit)](docs/Crime_in_Canada_Paper.pdf)**

---

## Tech Stack

- **Research:** Python (3.11+), Jupyter, pandas, NumPy, matplotlib/seaborn, scikit‑learn, pyarrow
- **API (planned):** Python (FastAPI/Flask), uvicorn
- **Frontend (WIP):** React + Vite, TypeScript/JavaScript, Recharts/D3, Tailwind (optional)
- **Hosting:** Vercel (frontend), TBD for the API

---

## Repository Structure

```text
crime-canada/
├─ api/            # Backend service (WIP) – endpoints for the dashboard
├─ frontend/       # Web UI (React/Vite, WIP) – filters, charts, tables
├─ research/       # Notebooks: EDA, preprocessing, baselines, experiments
└─ .gitignore
```

> As development progresses, you may add `data/` (raw/curated) and `docs/` (paper, figures).

---

## Data Sources

- **Statistics Canada – Crime & CSI tables (Ontario)** – Open Government Portal / StatCan tables
- **Toronto Police Service – Public Safety Data Portal** (for city‑level exploration)
- **Labour Force Survey (Ontario)** – Annual unemployment rates (contextual feature)

> Always review methodology notes, UCR definitions, release schedules, and data dictionaries before analysis.

---

## Methods & Experimental Design (from the paper)

- **Preprocessing**
  - Transpose/aggregate to feature‑wide matrices by year; remove >50%‑missing columns; impute remaining gaps within a violation; drop empty histories
  - Minimal scaling for tree models; standardization for regularized linear models
- **Target taxonomy** – **Violent**, **Property**, **Drug** (UCR‑aligned groupings)
- **Train/Test split** – Time‑based: train **≤2019**, test **2020–2023**
- **Special handling (Drugs)** – Account for **2018 legalization** via alternative training windows (e.g., train ≤2016), which improves out‑of‑sample validity
- **External feature** – Ontario unemployment rate (contextual; small lift vs. core policing metrics)

---

## Results (at a glance)

- **Complementary strengths:** Linear vs. ensemble methods — **no single model dominates** across all crime types
- **Low‑frequency categories:** **Ridge** is consistently strong
- **High‑volume categories:** **XGBoost/Extra Trees** excel (e.g., **property crime**, theft)
- **Decision Tree:** competitive for **property‑crime totals/theft** (simple, interpretable)
- **Robustness:** Reduced feature sets (Top‑10/Top‑5) retain competitive accuracy (ablation study)
- **Policy events matter:** Modeling quality improves when structural breaks (e.g., **Cannabis Act 2018**) are reflected in the training window

> See the paper’s tables/figures for detailed metrics and plots.

---

## Quickstart

### A) Explore the research notebooks

```bash
git clone https://github.com/MeetAdalaja/crime-canada.git
cd crime-canada/research
python -m venv .venv && source .venv/bin/activate   # (Windows) .venv\Scripts\activate
pip install -U pip wheel
pip install jupyter pandas numpy matplotlib seaborn scikit-learn pyarrow
jupyter lab
```

### B) Run the web app locally (WIP)

**Frontend**
```bash
cd frontend
npm install
npm run dev                 # Vite dev server
# npm run build && npm run preview
```

**API** (if/when available)
```bash
cd api
python -m venv .venv && source .venv/bin/activate   # (Windows) .venv\Scripts\activate
pip install -U pip
# pip install -r requirements.txt
# uvicorn app.main:app --reload
```

---

## Deploy (Vercel, SPA)

1. **Root Directory:** `frontend/`
2. **Framework preset:** Vite (or “Other”)
3. **Build command:** `npm run build`
4. **Output directory:** `dist`
5. **SPA rewrite:** create `vercel.json` at repo root:
   ```json
   { "rewrites": [{ "source": "/(.*)", "destination": "/index.html" }] }
   ```
6. Redeploy → **https://crime-ontario.vercel.app**

---

## Configuration

Create a local `.env` for dev if needed:

```ini
# API
API_PORT=8000
API_HOST=127.0.0.1
# FRONTEND (Vite)
VITE_API_BASE=http://127.0.0.1:8000
```

---

## Ethics & Limitations

- Forecasts reflect **reported** crime and **policing practices**, not all victimization
- Structural breaks (policy, pandemics) can **invalidate** naive time‑series assumptions
- Use responsibly: **decision support**, not deterministic prediction of individuals/places

---

## Roadmap

- [ ] Lock primary **data source(s)** and add dataset notes + download instructions
- [ ] Versioned **data artifacts** (`/data/curated/...`) + lightweight ETL
- [ ] Minimal **API** for charts
- [ ] **Frontend**: filters, line/bar charts, CSV/PNG export
- [ ] Optional **forecast** overlay with clear caveats
- [ ] CI: lint + notebook execution smoke test
- [ ] Deploy: Vercel (frontend) + host for API

---

## Citation

**Paper**
```bibtex
@inproceedings{adalaja2025crime,
  title     = {Machine Learning in Data-Driven Predictive Policing: Canada Perspective},
  author    = {Adalaja, Meet V. and Rahman, Md Zamilur and Begum, Khaleda},
  booktitle = {AII 2025 (Springer)},
  year      = {2025},
  note      = {Ontario, Canada; 1998--2023; ML models incl. Ridge, XGBoost, Extra Trees}
}
```

**Software**
```bibtex
@software{crime_canada_repo,
  author  = {Adalaja, Meet},
  title   = {Crime Canada — ML Forecasting \& Dashboard (Ontario-focused)},
  year    = {2025},
  url     = {https://github.com/MeetAdalaja/crime-canada}
}
```

---

## Acknowledgements

- Statistics Canada & Canadian open-data portals for accessible, high‑quality datasets
- The open‑source community for tools enabling reproducible analytics
