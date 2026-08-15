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
