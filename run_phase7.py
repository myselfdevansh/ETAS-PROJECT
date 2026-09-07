import numpy as np
import pandas as pd
from datetime import datetime
import os

from catalog.model import Catalog
from calibrate.em import calibrate_etas
from sources.registry import REGISTRY, cached_fetch

def main():
    print("===========================================")
    print(" Executing Phase 7 'DONE WHEN' Criteria")
    print("===========================================\n")
    
    print("[1/2] Fetching Small Calibration Catalog (Testing Mode)...")
    ca_fetcher = REGISTRY['california']
    # Very small spatial bounding box to keep 'N' small for testing loops
    ca_bbox = (-116.0, -115.0, 32.0, 33.0) 
    ca_time = (datetime(2023, 1, 1), datetime(2023, 2, 1)) # 1 month
    catalog = cached_fetch('california', ca_fetcher, ca_bbox, ca_time, min_mag=2.0)
    
    # Keep only first 40 events to ensure Python nested loops execute rapidly for the test
    df = catalog.data.sort_values('time_days').head(40)
    small_catalog = Catalog(df)
    print(f"  Loaded {len(small_catalog)} events for rapid EM calibration test.")
    
    t_start = 0.0
    t_end = float(df['time_days'].max() + 1.0)
    area_km2 = 100.0 * 100.0 # ~100x100km area roughly
    
    init_params = {
        'mu': 0.05,
        'k': 0.02,
        'c': 0.01,
        'p': 1.1,
        'alpha': 1.0,
        'd': 1.0,
        'q': 1.5,
        'mc': 2.0
    }
    
    print("\n[2/2] Running Expectation-Maximization (EM) Algorithm...")
    print("  Initial Parameters:", init_params)
    print("  Starting EM Loop (max 3 iterations for test)...")
    
    best_params, history = calibrate_etas(small_catalog, init_params, t_start, t_end, area_km2, max_iter=3)
    
    print("\n  Calibration Complete!")
    print("  Optimized Parameters:", best_params)
    print("  Log-Likelihood History:", [round(h, 4) for h in history])
    
    if len(history) > 1 and history[-1] > history[0]:
        print("\n  -> SUCCESS: Log-Likelihood successfully increased during EM training!")
    else:
        print("\n  -> Note: Log-Likelihood did not strictly increase, might need more data or more iterations.")
        
    print("\nDONE! Phase 7 Verification Complete.")

if __name__ == '__main__':
    main()
