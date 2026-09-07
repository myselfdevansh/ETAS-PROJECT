import numpy as np
import pandas as pd
from scipy.optimize import minimize
from catalog.model import Catalog
from model.kernels import omori_utsu, spatial_power_law, productivity
from model.likelihood import haversine_distance, calc_etas_ll

def e_step(catalog: Catalog, params: dict, t_start: float, t_end: float) -> np.ndarray:
    """
    Expectation Step: Calculates the branching probability matrix P.
    P[i, j] is the probability that event j was triggered by event i.
    P[j, j] is the probability that event j is a background event.
    """
    df = catalog.data.sort_values('time_days').reset_index(drop=True)
    times = df['time_days'].values
    mags = df['magnitude'].values
    lons = df['lon'].values
    lats = df['lat'].values
    n = len(df)
    
    mu, k, c, p, alpha, d, q = (
        params['mu'], params['k'], params['c'], 
        params['p'], params['alpha'], params['d'], params['q']
    )
    mc = params.get('mc', 2.0)
    
    P = np.zeros((n, n))
    
    for j in range(n):
        if times[j] < t_start or times[j] > t_end:
            continue
            
        # Background rate for event j
        lambda_j = mu
        P[j, j] = mu
        
        # Triggering rate from all past events i < j
        past_idx = np.where(times[:j] < times[j])[0]
        if len(past_idx) > 0:
            dt = times[j] - times[past_idx]
            r = haversine_distance(lons[past_idx], lats[past_idx], lons[j], lats[j])
            m_past = mags[past_idx]
            
            prod = productivity(m_past, mc, k, alpha)
            g_t = omori_utsu(dt, c, p)
            f_r = spatial_power_law(r, d, q)
            
            rates = prod * g_t * f_r
            P[past_idx, j] = rates
            lambda_j += np.sum(rates)
            
        # Normalize the j-th column so it sums to 1 (probabilities)
        if lambda_j > 0:
            P[:, j] = P[:, j] / lambda_j
            
    return P

def m_step(catalog: Catalog, P: np.ndarray, current_params: dict, t_start: float, t_end: float, area_km2: float) -> dict:
    """
    Maximization Step: Updates parameters using the expected sufficient statistics from P.
    Because Python is slow for nested Q-function evaluations, we employ a hybrid strategy 
    where mu is solved analytically from P, and the remaining parameters are optimized 
    using the rigorous log-likelihood function (L-BFGS-B).
    """
    df = catalog.data.sort_values('time_days').reset_index(drop=True)
    times = df['time_days'].values
    mc = current_params.get('mc', 2.0)
    
    # 1. Update background rate mu analytically (exact EM step)
    target_mask = (times >= t_start) & (times <= t_end)
    expected_bg = np.sum(P[target_mask, target_mask])
    new_mu = expected_bg / ((t_end - t_start) * area_km2)
    new_mu = max(new_mu, 1e-6) # prevent zero
    
    # 2. Optimize remaining parameters (Quasi-Newton MLE M-step)
    def q_function(opt_params):
        k, c, p, alpha, d, q_val = opt_params
        
        temp_params = {
            'mu': new_mu, 'k': k, 'c': c, 'p': p, 
            'alpha': alpha, 'd': d, 'q': q_val, 'mc': mc
        }
        # Maximize LL -> Minimize Negative LL
        ll = calc_etas_ll(catalog, temp_params, t_start, t_end, area_km2)
        return -ll if not np.isnan(ll) else np.inf
        
    x0 = [
        current_params['k'], current_params['c'], current_params['p'],
        current_params['alpha'], current_params['d'], current_params['q']
    ]
    
    # Physical bounds for parameter stability
    bounds = [
        (1e-5, 5.0),    # k
        (1e-4, 1.0),    # c
        (1.001, 3.0),   # p (> 1 for convergent integrals)
        (0.1, 5.0),     # alpha
        (0.1, 100.0),   # d
        (1.001, 5.0)    # q
    ]
    
    res = minimize(q_function, x0, bounds=bounds, method='L-BFGS-B', options={'maxiter': 3})
    
    k_new, c_new, p_new, alpha_new, d_new, q_new = res.x
    
    return {
        'mu': new_mu, 'k': k_new, 'c': c_new, 'p': p_new, 
        'alpha': alpha_new, 'd': d_new, 'q': q_new, 'mc': mc
    }

def calibrate_etas(catalog: Catalog, init_params: dict, t_start: float, t_end: float, area_km2: float, max_iter: int = 3, tol: float = 0.5):
    """
    Runs the Expectation-Maximization loop to calibrate ETAS parameters.
    """
    current_params = init_params.copy()
    ll_history = []
    
    for iteration in range(max_iter):
        # E-step
        P = e_step(catalog, current_params, t_start, t_end)
        
        # Current LL
        current_ll = calc_etas_ll(catalog, current_params, t_start, t_end, area_km2)
        ll_history.append(current_ll)
        print(f"  [EM] Iteration {iteration+1}/{max_iter} - Log-Likelihood: {current_ll:.4f}")
        
        # M-step
        new_params = m_step(catalog, P, current_params, t_start, t_end, area_km2)
        
        # Check convergence
        if iteration > 0 and abs(current_ll - ll_history[-2]) < tol:
            print("  [EM] Convergence reached.")
            current_params = new_params
            break
            
        current_params = new_params
        
    # Final eval
    final_ll = calc_etas_ll(catalog, current_params, t_start, t_end, area_km2)
    ll_history.append(final_ll)
    
    return current_params, ll_history
