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
