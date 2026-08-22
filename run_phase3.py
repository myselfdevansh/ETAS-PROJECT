import os
from datetime import datetime
from sources.registry import REGISTRY, cached_fetch
from viz.dashboard import create_eda_dashboard
import matplotlib.pyplot as plt

def main():
    print("===========================================")
    print(" Executing Phase 3 'DONE WHEN' Criteria")
    print("===========================================")

    # 1. California Catalog
    print("\n[1/2] Fetching California Catalog (USGS ComCat)...")
    ca_fetcher = REGISTRY['california']
    # Bounding box for California
    ca_bbox = (-125.0, -114.0, 32.0, 42.0) 
    ca_time = (datetime(2022, 1, 1), datetime(2023, 1, 1))
    ca_catalog = cached_fetch('california', ca_fetcher, ca_bbox, ca_time, min_mag=3.5)
    
    print(f"Loaded {len(ca_catalog)} events for California.")
    print("Generating California EDA Dashboard...")
    create_eda_dashboard(ca_catalog, "California")

    # 2. Non-US Catalog (Europe via EMSC)
    print("\n[2/2] Fetching Non-US Catalog (Europe EMSC)...")
    eu_fetcher = REGISTRY['europe_emsc']
    # Bounding box for Southern Europe / Med
    eu_bbox = (-10.0, 30.0, 35.0, 60.0)
    eu_time = (datetime(2022, 1, 1), datetime(2023, 1, 1))
    eu_catalog = cached_fetch('europe_emsc', eu_fetcher, eu_bbox, eu_time, min_mag=4.5)
    
    print(f"Loaded {len(eu_catalog)} events for Europe.")
    print("Generating Europe EDA Dashboard...")
    create_eda_dashboard(eu_catalog, "Europe")
    
    print("\nDONE! Figures should be located in docs/figures/")

if __name__ == "__main__":
    main()
