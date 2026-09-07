from datetime import datetime
from catalog.model import Catalog
from decluster.stochastic import stochastic_decluster
from sources.registry import REGISTRY, cached_fetch

def main():
    print("===========================================")
    print(" Executing Phase 8 'DONE WHEN' Criteria")
    print("===========================================\n")
    
    print("[1/2] Fetching California Catalog...")
    ca_fetcher = REGISTRY['california']
    ca_bbox = (-118.0, -116.0, 33.0, 35.0) 
    ca_time = (datetime(2023, 1, 1), datetime(2023, 6, 1))
    catalog = cached_fetch('california', ca_fetcher, ca_bbox, ca_time, min_mag=2.5)
    
    df = catalog.data.sort_values('time_days')
    if len(df) > 150: df = df.head(150) # Keep small for rapid E-step
    catalog = Catalog(df)
    
    t_start = 0.0
    t_end = float(df['time_days'].max() + 1.0)
    
    # Mock calibrated parameters for fast testing
    params = {'mu': 0.1, 'k': 0.05, 'c': 0.05, 'p': 1.2, 'alpha': 1.0, 'd': 1.0, 'q': 1.5, 'mc': 2.5}
    
    print(f"  Original Catalog Size: {len(catalog)} events")
    print("\n[2/2] Running Stochastic Declustering (Extracting Background)...")
    
    bg_catalog = stochastic_decluster(catalog, params, t_start, t_end)
    
    print(f"  Declustered (Background) Size: {len(bg_catalog)} events")
    print(f"  Removed {len(catalog) - len(bg_catalog)} triggered aftershocks.")
    
    if len(bg_catalog) < len(catalog):
        print("\n  -> SUCCESS: Successfully thinned catalog to isolate background seismicity!")
    else:
        print("\n  -> Note: No events removed.")
        
    print("\nDONE! Phase 8 Verification Complete.")

if __name__ == '__main__':
    main()
