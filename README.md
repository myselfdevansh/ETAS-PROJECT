<<<<<<< HEAD
# ETAS Toolkit

Earthquakes cluster in space and time, and the Epidemic-Type Aftershock Sequence (ETAS) is the standard statistical model for that clustering. This repository is a verified Python toolkit designed to acquire earthquake catalogs from global agencies, assess data quality, calibrate the ETAS model, simulate from it, and compute the probabilistic genealogy of triggered events[cite: 1]. 

## Repository Structure

* `sources/`: Catalog downloaders (FDSN + per-agency + scrapers)[cite: 1].
* `catalog/`: Data model, cleaning, deduplication, magnitude homogenization, and caching[cite: 1].
* `quality/`: Mc estimation (multiple methods), b-value, and QC[cite: 1].
* `viz/`: Plotting utilities (FMD, maps, time-mag, spatial Mc/b maps)[cite: 1].
* `model/`: Intensity, kernels, and likelihood (temporal + spatiotemporal)[cite: 1].
* `calibrate/`: E-step, M-step, EM driver, restarts, and KDE background field[cite: 1].
* `decluster/`: Stochastic declustering, rho_ij genealogy, and triggering graph[cite: 1].
* `simulate/`: Forward branching simulation and bootstrap[cite: 1].
* `evaluate/`: CSEP-style forecast tests[cite: 1].
* `features/`: Causal feature pipeline[cite: 1].
* `tests/`: Unit and regression test harness[cite: 1].
* `docs/`: Module documentation, notes, and regression reports[cite: 1].
* `notebooks/`: Exploratory analysis per region[cite: 1].
=======
# ETAS Toolkit Phase-1

A comprehensive Python library for statistical earthquake forecasting and analysis using the Epidemic-Type Aftershock Sequence (ETAS) model.

## Overview
This toolkit serves as an end-to-end forecasting pipeline to acquire, prepare, calibrate, and simulate earthquake catalogs. It standardizes raw data from global agencies and provides the foundational engine for testing machine-learning improvements to classical ETAS predictions.

## Phase 1: Catalog Ingestion Architecture
The project currently supports a robust data ingestion and standardization pipeline:
*   **Data Model**: Pandas-backed `Catalog` object with strictly enforced schemas.
*   **I/O Operations**: High-performance Parquet and CSV round-trip capabilities.
*   **QuakeML Parser**: Universal XML parser utilizing ObsPy to flatten complex nested FDSN event data.
*   **Spatial Math**: Azimuthal Equidistant (aeqd) coordinate transformations (spherical to planar Cartesian) using PyProj with < 1 meter error tolerance.
*   **Filter Engine**: Temporal, spatial, and magnitude filtering, plus automated deduplication.
*   **Local Cache**: Automatic local file caching to prevent redundant API calls and rate-limiting.

## Setup and Installation
This project requires Python 3.12+ and uses Conda for environment management.

```bash
conda create -n etas -c conda-forge python=3.12
conda activate etas
pip install -e .
>>>>>>> phase_1_setup
