# ETAS Toolkit — Handoff State

**Current Phase:** Phase 3 (Complete) $\rightarrow$ Phase 4 (Starting)

---

## 1. Done
* **Repository Skeleton:** Initialized the project directory tree (`catalog/`, `sources/`, `quality/`, `viz/`, `model/`, `calibrate/`, `decluster/`, `simulate/`, `evaluate/`, `features/`, `tests/`, `docs/`, `notebooks/`).
* **Phase 1 (Data Model & Ingestion):** Created the strict Pandas-backed `Catalog` object with high-performance Parquet/CSV round-trip, an ObsPy `QuakeML` XML parser, coordinate transforms, and a `~/.etas_cache/` caching architecture.
* **Phase 2 (Catalog Downloaders):** Built the `sources/` universal downloader CLI integrating 8 distinct endpoints:
  * *Clean APIs:* USGS ComCat, ISC, GCMT, GeoNet, EMSC, and AFAD.
  * *Scrapers:* Chile CSN (Zenodo static `.csv`) and Türkiye KOERI (HTML `<pre>` block parsing via `BeautifulSoup`).
  * Implemented recursive time-window chunking in the FDSN client to automatically bypass the 20,000-event request caps.
* **Phase 3 (Visualization Utilities):** Built the `viz/` module for Exploratory Data Analysis (EDA):
  * `fmd.py`: Gutenberg-Richter frequency-magnitude distributions.
  * `maps.py`: `cartopy`-powered geographic epicenter maps scaling markers by magnitude.
  * `time.py` & `interevent.py`: Cumulative seismicity, time-magnitude stem plots, inter-event clustering times, and cumulative moment release.
  * `dashboard.py`: A `create_eda_dashboard()` capstone function combining all plots into a 6-panel summary figure.

## 2. Verified
* **Phase 2 Pipeline Resilience:** Verified that network downloads correctly fall back to the cache layer, and handled FDSN HTTP 204 (No Data) errors to prevent crashes on empty catalog returns.
* **Phase 3 Generation:** Successfully generated and saved the multi-panel EDA dashboards for California and Europe (EMSC) to `docs/figures/`.

## 3. In Progress
* Preparing for **Phase 4: Magnitude of completeness ($M_c$) — many methods** (`quality/mc.py`).
  * Planning implementations for Maximum Curvature (MAXC), Goodness-of-fit test (GFT), and b-value stability (MBS).

## 4. Uncertain
* The scaffolded authenticated scrapers for Japan (JMA) and Taiwan (CWA) currently return safe, empty catalogs. Live extraction requires injecting account credentials via `.env` variables if those regions are strictly required for future runs.
