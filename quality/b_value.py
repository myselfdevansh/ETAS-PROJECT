import numpy as np
import pandas as pd
from typing import Tuple
from catalog.model import Catalog

def calc_b_aki_utsu(catalog: Catalog, mc: float, bin_width: float = 0.1) -> Tuple[float, float]:
    """
    Calculates the b-value using the standard Aki-Utsu Maximum Likelihood Estimator.
    Assumes a continuous magnitude distribution.
    
    Returns:
        (b_value, shi_bolt_uncertainty)
    """
    mags = catalog.data['magnitude'].dropna()
    mags_above = mags[mags >= mc - (bin_width / 2.0)]
    
    n_obs = len(mags_above)
    if n_obs < 2:
        return np.nan, np.nan
        
    mean_mag = np.mean(mags_above)
    
    # Aki-Utsu MLE formula
    b_value = np.log10(np.exp(1)) / (mean_mag - (mc - bin_width / 2.0))
    
    # Shi & Bolt (1982) robust uncertainty estimation
    variance_m = np.sum((mags_above - mean_mag)**2) / (n_obs - 1)
    unc = 2.30 * (b_value**2) * np.sqrt(variance_m / n_obs)
    
    return round(b_value, 4), round(unc, 4)

def calc_b_tinti(catalog: Catalog, mc: float, bin_width: float = 0.1) -> Tuple[float, float]:
    """
    Calculates the b-value using the robust Tinti & Mulargia (1987) method.
    Specifically accounts for the mathematical effect of artificial magnitude binning,
    which is critical for modern digital seismic networks.
    
    Returns:
        (b_value, uncertainty)
    """
    mags = catalog.data['magnitude'].dropna()
    # Strictly applying Mc boundary
    mags_above = mags[mags >= mc - (bin_width / 2.0)]
    
    n_obs = len(mags_above)
    if n_obs < 2:
        return np.nan, np.nan
        
    mean_mag = np.mean(mags_above)
    
    # Tinti & Mulargia formula for apparent (binned) magnitudes
    p = 1.0 + bin_width / (mean_mag - mc)
    
    if p <= 0:
        return np.nan, np.nan
        
    b_value = np.log(p) / (bin_width * np.log(10))
    
    # Standard error approximation for the Tinti estimator
    unc = (1 - p) / (np.sqrt(n_obs * p) * bin_width * np.log(10))
    # Taking absolute value in case of negative uncertainty representation
    unc = abs(unc)
    
    return round(b_value, 4), round(unc, 4)
