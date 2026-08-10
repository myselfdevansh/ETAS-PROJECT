# ETAS Toolkit — Handoff State

**Current Phase:** Phase 0 (Complete) $\rightarrow$ Phase 1 (Starting)

---

## 1. Done
* **Repository Skeleton:** Initialized the project directory tree (`catalog/`, `sources/`, `quality/`, `viz/`, `model/`, `calibrate/`, `decluster/`, `simulate/`, `evaluate/`, `features/`, `tests/`, `docs/`, `notebooks/`).
* **Configuration:** Initialized `README.md` detailing the toolkit structure and `pyproject.toml` specifying all core dependencies (`numpy`, `scipy`, `pandas`, `obspy`, `cartopy`, `seismostats`, etc.)[cite: 1, 2].
* **Catalog Survey:** Completed `docs/catalog_survey.md` detailing global aggregators and regional earthquake catalog sources.

## 2. Verified
* **Survey Coverage:** Documented 17 catalog sources across all 8 project regions (California, Japan, Italy, Chile, Greece, Türkiye, New Zealand, Taiwan) plus global aggregators[cite: 1].
* **Classification:** Correctly identified clean FDSN APIs vs. "hard" sources requiring scrapers or authentication (Japan JMA/NIED, Chile CSN, Taiwan CWA GDMS, INGV HORUS)[cite: 1].
* **API Constraints:** Documented technical caps, such as the 20,000-event limit on USGS ComCat[cite: 1].

## 3. In Progress
* Staging, committing, and pushing Phase 0 work to the `phase-0-setup` branch for PR review[cite: 1].
* Preparing for **Phase 1: Catalog Data Model & Ingestion Architecture** (`catalog/model.py`, `catalog/quakeml.py`, `catalog/projection.py`, `catalog/clean.py`, and local disk caching)[cite: 1].

## 4. Uncertain
* None for Phase 0. *(Scraper rate limits and authentication handling for JMA/CSN/CWA will be evaluated during Phase 2 downloader implementation)*[cite: 1].
