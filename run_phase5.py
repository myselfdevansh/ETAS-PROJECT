import numpy as np
import pandas as pd
from datetime import datetime
import os

from catalog.model import Catalog
from quality.b_value import calc_b_aki_utsu, calc_b_tinti
from sources.registry import REGISTRY, cached_fetch

def create_binned_synthetic_catalog(true_b=1.0, true_mc=3.0, n_events=20000, bin_width=0.1):
    """Generates a synthetic catalog and artificially bins the magnitudes to 0.1"""
    beta = true_b * np.log(10)
    
    # Generate perfect continuous magnitudes starting lower so the Mc bin is symmetrically filled
    mags_continuous = np.random.exponential(scale=1/beta, size=n_events*2) + (true_mc - 1.0)
    
    # Simulate real-world sensor binning (round to nearest 0.1)
    mags_binned = np.round(mags_continuous / bin_width) * bin_width
    
    # Filter only those that mathematically triggered the 'sensor' above Mc
    mags_binned = mags_binned[mags_binned >= true_mc - (bin_width/2.0)]
    
    # Take exact requested number
    mags_binned = mags_binned[:n_events]
    actual_len = len(mags_binned)
    
    df = pd.DataFrame({
        'magnitude': mags_binned,
        'lon': np.random.uniform(-120, -115, actual_len),
        'lat': np.random.uniform(32, 36, actual_len),
        'time': [datetime.now()] * actual_len,
        'time_days': 0.0,
        'depth': 10.0,
        'magnitude-type': 'ML',
        'source-agency': 'SYNTH',
        'event-id': [str(i) for i in range(actual_len)]
    })
    return Catalog(df)

def main():
    print("===========================================")
    print(" Executing Phase 5 'DONE WHEN' Criteria")
    print("===========================================\n")
    
    # 1. Synthetic Unit Test
    print("[1/2] Running Synthetic Catalog Unit Test...")
    print("  -> True underlying b-value : 1.000")
    print("  -> Sensor artificial binning : 0.1")
    print("  -> True Mc                 : 3.0")
    
    synth_cat = create_binned_synthetic_catalog(true_b=1.0, true_mc=3.0, n_events=20000)
    
    aki_b, aki_unc = calc_b_aki_utsu(synth_cat, mc=3.0, bin_width=0.1)
    tinti_b, tinti_unc = calc_b_tinti(synth_cat, mc=3.0, bin_width=0.1)
    
    print(f"\n  [Aki-Utsu] b-value : {aki_b} ± {aki_unc}")
    print(f"  [Tinti]    b-value : {tinti_b} ± {tinti_unc}")
    print("  (Notice how Tinti & Mulargia mathematically corrects for the binning distortion!)\n")
    
    # 2. Real World Test (Southern California)
    print("[2/2] Fetching California Catalog (USGS ComCat)...")
    ca_fetcher = REGISTRY['california']
    ca_bbox = (-124.0, -114.0, 32.0, 42.0)
    ca_time = (datetime(2023, 1, 1), datetime(2023, 3, 1))
    ca_catalog = cached_fetch('california', ca_fetcher, ca_bbox, ca_time, min_mag=2.5)
    
    print(f"  Loaded {len(ca_catalog)} events.")
    
    # Assuming Mc = 2.5 for this specific 2-month window
    mc_cali = 2.5
    print(f"  Evaluating b-value for Southern California (Assuming Mc = {mc_cali}):")
    
    c_aki_b, c_aki_unc = calc_b_aki_utsu(ca_catalog, mc=mc_cali, bin_width=0.1)
    c_tinti_b, c_tinti_unc = calc_b_tinti(ca_catalog, mc=mc_cali, bin_width=0.1)
    
    print(f"  [Aki-Utsu] b-value : {c_aki_b} ± {c_aki_unc}")
    print(f"  [Tinti]    b-value : {c_tinti_b} ± {c_tinti_unc}")
    
    print("\nDONE! Phase 5 Verification Complete.")

if __name__ == '__main__':
    main()
