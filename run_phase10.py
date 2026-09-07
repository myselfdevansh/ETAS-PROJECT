from datetime import datetime
from catalog.model import Catalog
from sources.registry import REGISTRY, cached_fetch
from calibrate.em import calibrate_etas
from evaluate.csep import expected_events, n_test

def main():
    print("===========================================")
    print(" Executing Phase 10 'DONE WHEN' Criteria")
    print("===========================================\n")
    
    print("[1/3] Fetching California Catalog...")
    ca_fetcher = REGISTRY['california']
    ca_bbox = (-117.0, -115.0, 32.0, 34.0) 
    ca_time = (datetime(2023, 1, 1), datetime(2023, 4, 1)) # 3 months
    catalog = cached_fetch('california', ca_fetcher, ca_bbox, ca_time, min_mag=2.5)
    
    df = catalog.data.sort_values('time_days').reset_index(drop=True)
    
    # Split: First 2 months training, last 1 month testing
    train_end = float(df['time_days'].max() * (2/3))
    t_end = float(df['time_days'].max() + 1.0)
    
    df_train = df[df['time_days'] < train_end]
    df_test = df[df['time_days'] >= train_end]
    
    train_cat = Catalog(df_train)
    
    print(f"  Training Window: 0.0 to {train_end:.1f} days ({len(df_train)} events)")
    print(f"  Testing Window : {train_end:.1f} to {t_end:.1f} days ({len(df_test)} events)")
    
    area = 100.0 * 100.0
    
    print("\n[2/3] Training ETAS Model on Training Window...")
    init = {'mu': 0.1, 'k': 0.02, 'c': 0.05, 'p': 1.1, 'alpha': 1.0, 'd': 1.0, 'q': 1.5, 'mc': 2.5}
    best, _ = calibrate_etas(train_cat, init, 0.0, train_end, area, max_iter=2)
    
    print("\n[3/3] Running CSEP N-Test on Testing Window...")
    n_exp = expected_events(train_cat, best, train_end, t_end, area)
    n_obs = len(df_test)
    
    print(f"  Expected events (N_exp) : {n_exp:.2f}")
    print(f"  Observed events (N_obs) : {n_obs}")
    
    d1, d2 = n_test(n_obs, n_exp)
    print(f"  delta_1 (under-predict) : {d1:.4f}")
    print(f"  delta_2 (over-predict)  : {d2:.4f}")
    
    if d1 < 0.025 or d2 < 0.025:
        print("  -> Result: FAIL (Model rejected at 95% confidence)")
    else:
        print("  -> Result: PASS (Model forecast is statistically consistent with observations)")
        
    print("\nDONE! Phase 10 Verification Complete.")

if __name__ == '__main__':
    main()
