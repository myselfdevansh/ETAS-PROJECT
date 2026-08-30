import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import os

from catalog.model import Catalog
from sources.registry import REGISTRY, cached_fetch
from quality.mc import calc_maxc, calc_gft, calc_mbs, calc_emr, calc_mbass
from quality.mc_map import calculate_mc_grid

def create_synthetic_catalog(true_mc=3.0, b_value=1.0, n_events=5000):
    """Generates a synthetic catalog with a known Mc."""
    # Perfect GR above Mc
    beta = b_value * np.log(10)
    mags_above = np.random.exponential(scale=1/beta, size=int(n_events * 0.7)) + true_mc
    
    # Incomplete below Mc (simulating detection drop-off)
    mags_below = np.random.normal(loc=true_mc - 0.5, scale=0.3, size=int(n_events * 0.3))
    mags_below = mags_below[mags_below < true_mc]
    
    mags = np.concatenate([mags_above, mags_below])
    
    # Create dummy dataframe
    df = pd.DataFrame({
        'magnitude': mags,
        'lon': np.random.uniform(-120, -115, len(mags)),
        'lat': np.random.uniform(32, 36, len(mags)),
        'time': [datetime.now()] * len(mags),
        'time_days': 0.0,
        'depth': 10.0,
        'magnitude-type': 'ML',
        'source-agency': 'SYNTH',
        'event-id': [str(i) for i in range(len(mags))]
    })
    return Catalog(df)

def main():
    os.makedirs('docs/figures', exist_ok=True)
    
    print("===========================================")
    print(" Executing Phase 4 'DONE WHEN' Criteria")
    print("===========================================\n")
    
    # 1. Synthetic Test
    print("[1/3] Running Synthetic Catalog Unit Test (True Mc = 3.0)...")
    synth_cat = create_synthetic_catalog(true_mc=3.0)
    print(f"  MAXC  : {calc_maxc(synth_cat)}")
    print(f"  GFT   : {calc_gft(synth_cat)}")
    print(f"  MBS   : {calc_mbs(synth_cat)}")
    print(f"  EMR   : {calc_emr(synth_cat)}")
    print(f"  MBASS : {calc_mbass(synth_cat)}")
    print("  -> Synthetic tests complete.\n")
    
    # 2. Southern California Catalog
    print("[2/3] Fetching California Catalog (USGS ComCat)...")
    ca_fetcher = REGISTRY['california']
    ca_bbox = (-124.0, -114.0, 32.0, 42.0)
    # Fetch a smaller window for Phase 4 to keep tests fast, but with low min_mag
    ca_time = (datetime(2023, 1, 1), datetime(2023, 3, 1))
    ca_catalog = cached_fetch('california', ca_fetcher, ca_bbox, ca_time, min_mag=1.0)
    
    print(f"  Loaded {len(ca_catalog)} events.")
    print("  Evaluating Mc for Southern California:")
    print(f"  MAXC  : {calc_maxc(ca_catalog)}")
    print(f"  GFT   : {calc_gft(ca_catalog)}")
    print(f"  MBS   : {calc_mbs(ca_catalog)}")
    print(f"  EMR   : {calc_emr(ca_catalog)}")
    print(f"  MBASS : {calc_mbass(ca_catalog)}")
    print("  -> Real-world multi-method evaluation complete.\n")
    
    # 3. Spatial Mc Mapping
    print("[3/3] Rendering Spatial Mc Map for California...")
    # Reduce dataset slightly for speed if needed, but KDTree is fast
    grid_df = calculate_mc_grid(ca_catalog, method='MAXC', grid_spacing=0.5, n_events=150)
    
    # Plotting
    import cartopy.crs as ccrs
    import cartopy.feature as cfeature
    
    plt.figure(figsize=(10, 8))
    ax = plt.axes(projection=ccrs.Mercator())
    ax.set_extent([-124.0, -114.0, 32.0, 42.0], crs=ccrs.PlateCarree())
    ax.add_feature(cfeature.COASTLINE)
    ax.add_feature(cfeature.BORDERS)
    ax.add_feature(cfeature.STATES, linestyle=':')
    
    # Scatter plot of the grid points colored by Mc
    sc = ax.scatter(grid_df['lon'], grid_df['lat'], c=grid_df['mc'], 
                    cmap='viridis_r', s=150, marker='s', alpha=0.8, transform=ccrs.PlateCarree())
    
    plt.colorbar(sc, label='Magnitude of Completeness (Mc)')
    plt.title('Spatial Variation of Mc in California (MAXC method)')
    
    out_path = 'docs/figures/mc_map_california.png'
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    print(f"  Map rendered successfully to {out_path}\n")
    
    print("DONE! Phase 4 Verification Complete.")

if __name__ == '__main__':
    main()
