# ETAS Toolkit

A comprehensive Python library for statistical earthquake forecasting and analysis using the Epidemic-Type Aftershock Sequence (ETAS) model. Earthquakes cluster in space and time, and ETAS is the standard statistical model for that clustering. 

This repository is a verified Python toolkit designed to acquire earthquake catalogs from global agencies, assess data quality, calibrate the ETAS model, simulate from it, and compute the probabilistic genealogy of triggered events.

## Setup and Installation
This project requires Python 3.12+ and uses Conda for environment management.

```bash
conda create -n etas -c conda-forge python=3.12
conda activate etas
pip install -e .
```

## Phase 1: Catalog Ingestion Architecture
The project currently supports a robust data ingestion and standardization pipeline:
* **Data Model**: Pandas-backed `Catalog` object with strictly enforced schemas.
* **I/O Operations**: High-performance Parquet and CSV round-trip capabilities.
* **QuakeML Parser**: Universal XML parser utilizing ObsPy to flatten complex nested FDSN event data.
* **Spatial Math**: Azimuthal Equidistant (aeqd) coordinate transformations using PyProj.
* **Local Cache**: Automatic local file caching (`~/.etas_cache/`) to prevent redundant API calls.

## Phase 2: Catalog Downloaders (Acquisition Module)
The toolkit provides a unified Universal Downloader that bridges multiple international earthquake agencies into a single interface. 
You can fetch normalized data from 8 different global and regional endpoints using our CLI!

### Supported Sources
* **Clean APIs:** `california` (USGS ComCat), `global_isc` (ISC), `europe_emsc` (EMSC), `new_zealand` (GeoNet), `turkiye_afad` (AFAD JSON), `global_gcmt` (GCMT NDK parsing).
* **Scrapers:** `chile_scrape` (Zenodo ZIP extraction), `turkiye_koeri_scrape` (HTML `<pre>` block parser).

### CLI Usage Example
The sources registry includes an automated time-window chunking feature that easily bypasses the USGS 20,000-event cap! It also passes all network requests through the Phase 1 caching engine automatically.
```bash
python -m sources.registry --region california --from_date 2010-01-01 --to_date 2020-01-01 --min-mag 2.5
```

## Repository Structure
* `sources/`: Catalog downloaders (FDSN + per-agency + scrapers)
* `catalog/`: Data model, cleaning, deduplication, caching
* `quality/`: Mc estimation, b-value, QC
* `viz/`: Plotting utilities (FMD, maps, time-mag, spatial Mc/b maps)
* `model/`: Intensity, kernels, likelihood (temporal + spatiotemporal)
* `calibrate/`: E-step, M-step, EM driver, restarts, KDE background field
* `decluster/`: Stochastic declustering, rho_ij genealogy, triggering graph
* `simulate/`: Forward branching simulation and bootstrap
* `evaluate/`: CSEP-style forecast tests
* `features/`: Causal feature pipeline
* `tests/`: Unit and regression test harness
* `docs/`: Module documentation, notes, regression reports
* `notebooks/`: Exploratory analysis per region
