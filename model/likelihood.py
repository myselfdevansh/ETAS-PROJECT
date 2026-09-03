import numpy as np
import pandas as pd
from catalog.model import Catalog
from model.kernels import omori_utsu, omori_integral, spatial_power_law, productivity

def haversine_distance(lon1, lat1, lon2, lat2):
    """Calculate distance in km between two points on earth."""
    R = 6371.0 # Earth radius in km
    lat1_rad, lon1_rad = np.radians(lat1), np.radians(lon1)
    lat2_rad, lon2_rad = np.radians(lat2), np.radians(lon2)
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    a = np.sin(dlat/2)**2 + np.cos(lat1_rad) * np.cos(lat2_rad) * np.sin(dlon/2)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
    return R * c

def calc_etas_ll(catalog: Catalog, params: dict, t_start: float, t_end: float, area_km2: float) -> float:
    """
    Calculates the exact ETAS log-likelihood for a catalog.
    
    Args:
        catalog: The Catalog object containing earthquakes.
        params: Dictionary of ETAS parameters (mu, k, c, p, alpha, d, q).
        t_start: Start of the target evaluation window (in days).
        t_end: End of the target evaluation window (in days).
        area_km2: The spatial area of the domain in square kilometers.
        
    Returns:
        The scalar log-likelihood.
    """
    df = catalog.data.sort_values('time_days').reset_index(drop=True)
    target_df = df[(df['time_days'] >= t_start) & (df['time_days'] <= t_end)]
    
    mu, k, c, p, alpha, d, q = (
        params['mu'], params['k'], params['c'], 
        params['p'], params['alpha'], params['d'], params['q']
    )
    mc = params.get('mc', 2.0)
    
    times = df['time_days'].values
    mags = df['magnitude'].values
    lons = df['lon'].values
    lats = df['lat'].values
    
    target_indices = target_df.index.values
    
    log_likelihood = 0.0
    
    # 1. Sum of log intensities at each target event
    for j in target_indices:
        t_j = times[j]
        if t_j < t_start or t_j > t_end: continue
        
        past_idx = np.where(times < t_j)[0]
        
        if len(past_idx) == 0:
            intensity_j = mu
        else:
            dt = t_j - times[past_idx]
            r = haversine_distance(lons[past_idx], lats[past_idx], lons[j], lats[j])
            m_past = mags[past_idx]
            
            prod = productivity(m_past, mc, k, alpha)
            g_t = omori_utsu(dt, c, p)
            f_r = spatial_power_law(r, d, q)
            
            intensity_j = mu + np.sum(prod * g_t * f_r)
        
        log_likelihood += np.log(intensity_j)
        
    # 2. Subtract the integral of the intensity over the space-time window
    T = t_end - t_start
    integral = mu * T * area_km2
    
    for i in range(len(df)):
        t_i = times[i]
        if t_i >= t_end:
            break
            
        int_start = max(0.0, t_start - t_i)
        int_end = t_end - t_i
        
        if int_end > 0:
            prod = productivity(mags[i], mc, k, alpha)
            # Assuming spatial integral integrates to 1 over infinite domain
            temporal_int = omori_integral(int_end, c, p) - omori_integral(int_start, c, p)
            integral += prod * temporal_int
            
    log_likelihood -= integral
    return log_likelihood
