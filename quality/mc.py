import numpy as np
import pandas as pd
from scipy.stats import norm
from scipy.optimize import minimize
from catalog.model import Catalog

def calc_maxc(catalog: Catalog, bin_width: float = 0.1, correction: float = 0.2) -> float:
    """
    Maximum Curvature (MAXC) method with empirical correction.
    Reference: Wiemer & Wyss (2000).
    Finds the magnitude bin with the highest frequency of events and adds a safety correction.
    """
    mags = catalog.data['magnitude'].dropna()
    if len(mags) == 0:
        return np.nan
        
    bins = np.arange(np.floor(mags.min()*10)/10, np.ceil(mags.max()*10)/10 + bin_width, bin_width)
    counts, edges = np.histogram(mags, bins=bins)
    
    max_idx = np.argmax(counts)
    mc_raw = edges[max_idx] # left edge of the bin with max counts
    
    return round(mc_raw + correction, 2)

def _calc_b_aki_utsu(mags: np.ndarray, mc: float, bin_width: float = 0.1) -> float:
    """Helper to calculate b-value using Aki-Utsu maximum likelihood."""
    mags_above = mags[mags >= mc - (bin_width / 2.0)]
    if len(mags_above) < 2:
        return np.nan
    mean_mag = np.mean(mags_above)
    b_value = np.log10(np.exp(1)) / (mean_mag - (mc - bin_width / 2.0))
    return b_value

def calc_gft(catalog: Catalog, bin_width: float = 0.1, threshold: float = 90.0) -> float:
    """
    Goodness-of-Fit Test (GFT) method.
    Reference: Wiemer & Wyss (2000).
    Compares the observed FMD with a synthetic Gutenberg-Richter distribution.
    Returns the lowest Mc where the fit is >= threshold (usually 90% or 95%).
    """
    mags = catalog.data['magnitude'].dropna()
    if len(mags) < 10:
        return np.nan
        
    bins = np.arange(np.floor(mags.min()*10)/10, np.ceil(mags.max()*10)/10 + bin_width, bin_width)
    mc_candidates = bins[:-1]
    
    for mc_cand in mc_candidates:
        mags_above = mags[mags >= mc_cand - (bin_width / 2.0)]
        n_obs = len(mags_above)
        if n_obs < 10:
            continue
            
        b_val = _calc_b_aki_utsu(mags, mc_cand, bin_width)
        if np.isnan(b_val):
            continue
            
        # Create Synthetic GR
        a_val = np.log10(n_obs) + b_val * mc_cand
        
        # Calculate observed and expected cumulative counts
        obs_counts, _ = np.histogram(mags_above, bins=bins[bins >= mc_cand])
        obs_cum = np.cumsum(obs_counts[::-1])[::-1]
        
        # Expected cumulative counts
        m_centers = bins[bins >= mc_cand][:-1]
        exp_cum = 10**(a_val - b_val * m_centers)
        
        # Calculate Goodness of fit R
        R = 100.0 - (np.sum(np.abs(obs_cum - exp_cum)) / np.sum(obs_cum)) * 100.0
        
        if R >= threshold:
            return round(mc_cand, 2)
            
    return np.nan

def calc_mbs(catalog: Catalog, bin_width: float = 0.1) -> float:
    """
    b-value Stability (MBS) method.
    Reference: Cao & Gao (2002); Woessner & Wiemer (2005).
    Finds the lowest Mc where the b-value change is within the Shi-Bolt uncertainty.
    """
    mags = catalog.data['magnitude'].dropna()
    if len(mags) < 10:
        return np.nan
        
    bins = np.arange(np.floor(mags.min()*10)/10, np.ceil(mags.max()*10)/10 + bin_width, bin_width)
    mc_candidates = bins[:-1]
    
    b_values = []
    shi_bolt_unc = []
    
    for mc_cand in mc_candidates:
        mags_above = mags[mags >= mc_cand - (bin_width / 2.0)]
        n_obs = len(mags_above)
        if n_obs < 10:
            b_values.append(np.nan)
            shi_bolt_unc.append(np.nan)
            continue
            
        b_val = _calc_b_aki_utsu(mags, mc_cand, bin_width)
        b_values.append(b_val)
        
        # Shi-Bolt uncertainty (simplified)
        std_m = np.std(mags_above)
        unc = 2.30 * (b_val**2) * std_m / np.sqrt(n_obs * (n_obs - 1)) if n_obs > 1 else np.nan
        shi_bolt_unc.append(unc)
        
    # Find stability point
    for i in range(len(b_values) - 1):
        if np.isnan(b_values[i]) or np.isnan(shi_bolt_unc[i]):
            continue
        
        if abs(b_values[i] - b_values[i+1]) <= shi_bolt_unc[i]:
            return round(mc_candidates[i], 2)
            
    return np.nan


def calc_emr(catalog: Catalog, bin_width: float = 0.1) -> float:
    """
    Entire-Magnitude-Range (EMR) method.
    Reference: Woessner and Wiemer (2005).
    Fits a GR model + Cumulative Normal detection probability using Maximum Likelihood.
    """
    mags = catalog.data['magnitude'].dropna()
    if len(mags) < 50:
        return np.nan

    bins = np.arange(np.floor(mags.min()*10)/10, np.ceil(mags.max()*10)/10 + bin_width, bin_width)
    counts, edges = np.histogram(mags, bins=bins)
    m_centers = edges[:-1] + bin_width / 2.0

    if len(counts) < 5: 
        return np.nan
    
    max_idx = np.argmax(counts)
    mc_guess = m_centers[max_idx]
    
    def emr_nll(params):
        mc, mu, sigma, b = params
        if sigma <= 0 or b <= 0 or mc < m_centers[0] or mc > m_centers[-1]:
            return np.inf
            
        # Detection probability (cumulative normal)
        Pd = norm.cdf(m_centers, loc=mu, scale=sigma)
        
        # Theoretical GR rates anchored at the max count
        a_val = np.log10(max(1, counts[max_idx])) + b * mc
        lambda_gr = 10**(a_val - b * m_centers)
        
        expected = lambda_gr * Pd
        expected = np.maximum(expected, 1e-10) # avoid log(0)
        
        # Poisson negative log-likelihood
        nll = np.sum(expected - counts * np.log(expected))
        return nll

    # Initial guesses: [Mc, mu, sigma, b_value]
    init_guess = [mc_guess, mc_guess - 0.5, 0.3, 1.0]
    
    res = minimize(emr_nll, init_guess, method='Nelder-Mead', options={'maxiter': 1000})
    
    if res.success:
        return round(res.x[0], 2)
    return np.nan

def calc_mbass(catalog: Catalog, bin_width: float = 0.1) -> float:
    """
    MBASS (Median-Based Analysis of the Segment Slope) method.
    Reference: Amorese (2007).
    Finds the magnitude where the median slope of the FMD changes most drastically.
    """
    mags = catalog.data['magnitude'].dropna()
    if len(mags) < 50:
        return np.nan
        
    bins = np.arange(np.floor(mags.min()*10)/10, np.ceil(mags.max()*10)/10 + bin_width, bin_width)
    counts, edges = np.histogram(mags, bins=bins)
    
    # Non-cumulative FMD log-counts
    log_counts = np.log10(np.maximum(counts, 1))
    
    # Differences between successive bins (slopes)
    slopes = np.diff(log_counts)
    mc_candidates = edges[1:-1]
    
    if len(slopes) < 4:
        return np.nan
        
    max_diff = -1
    best_mc = np.nan
    
    # Iterate over possible breakpoints to find maximum median difference
    for i in range(2, len(slopes) - 2):
        left_slopes = slopes[:i]
        right_slopes = slopes[i:]
        
        diff = abs(np.median(left_slopes) - np.median(right_slopes))
        
        if diff > max_diff:
            max_diff = diff
            best_mc = mc_candidates[i]
            
    return round(best_mc + bin_width / 2.0, 2) if not np.isnan(best_mc) else np.nan
