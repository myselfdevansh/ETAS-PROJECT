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

## Phase 3: Visualization Utilities (Exploratory Data Analysis)
The `viz/` module handles all plotting and geographical rendering for the catalogs.
* **Frequency-Magnitude Distribution (`fmd.py`)**: Plots the Gutenberg-Richter distribution (cumulative and incremental).
* **Epicenter Maps (`maps.py`)**: Renders geographical maps using `cartopy`, automatically scaling markers by magnitude and coloring by depth.
* **Temporal Evolution (`time.py` & `interevent.py`)**: Plots cumulative seismicity, time-magnitude stem plots, inter-event time distributions, and cumulative moment release.
* **Spatial Cross-Sections (`space.py`)**: Depth vs. Longitude profiles.
* **Multi-Panel Dashboards (`dashboard.py`)**: A single capstone function `create_eda_dashboard()` generates a complete EDA summary figure for any region and saves it to `docs/figures/`.


## Phase 4: Magnitude of Completeness ($)
Before the ETAS model can be calibrated, the network's completeness threshold must be established. The quality/ module implements comprehensive statistical methods for this:
* **Estimators (mc.py)**: Includes MAXC (Maximum Curvature), GFT (Goodness-of-Fit Test), MBS ($-value Stability), EMR (Entire-Magnitude-Range), and MBASS (Median-based slope change).
* **Spatial Mapping (mc_map.py)**: Utilizes a scipy.spatial.cKDTree to map geographic $ variations across regions using constant-N nearest-neighbor sampling.
\n
## Phase 5: Estimating the $b$-value
The `quality/b_value.py` module accurately calculates the Gutenberg-Richter $b$-value, a critical prior for ETAS modeling:
* **Aki-Utsu**: Standard maximum likelihood estimation.
* **Tinti & Mulargia**: Robust estimation that mathematically corrects for the artificial magnitude binning present in modern digital seismic networks.
* **Shi & Bolt Uncertainty**: Rigorous statistical bounds ($\pm \sigma$) applied to the estimates.
\n
## Phase 6: ETAS Model Formulation & Likelihood
The `model/` module contains the mathematical heart of the Epidemic-Type Aftershock Sequence process:
* **Kernels (`kernels.py`)**: Implements the temporal Omori-Utsu decay $(t+c)^{-p}$, the spatial power-law distance decay, and the exponential productivity law.
* **Likelihood Engine (`likelihood.py`)**: A robust spatial-temporal integral evaluator that calculates the exact ETAS log-likelihood over a given catalog for any set of ETAS parameters.
\n
## Phase 7: ETAS Calibration (EM Algorithm)
The `calibrate/em.py` module trains the ETAS model to learn the optimal triggering parameters for any given earthquake catalog using Expectation-Maximization:
* **E-Step**: Computes the full $N \times N$ triggering probability matrix (who triggered whom).
* **M-Step**: Uses numerical optimization (L-BFGS-B) bounded by the probabilities to maximize the expected complete-data log-likelihood.
\n
## Phase 8: Stochastic Declustering
The `decluster/stochastic.py` module isolates independent background earthquakes by probabilistically filtering out triggered aftershocks. It utilizes the branching probability matrix $P_{ij}$ calculated by the ETAS E-step.


## Phase 9: Simulation & Bootstrapping
The `simulate/branching.py` module uses Monte Carlo methods and inverse transform sampling to mathematically forward-simulate synthetic ETAS catalogs, generating both spontaneous background activity and multi-generational triggered aftershock sequences.


## Phase 10: Evaluation & CSEP Testing
The `evaluate/csep.py` module introduces rigorous statistical testing (based on the Collaboratory for the Study of Earthquake Predictability frameworks). It evaluates ETAS forecasts against real-world validation data using tests like the Poisson N-test to ensure the model doesn't systematically over or under-predict seismicity.

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
