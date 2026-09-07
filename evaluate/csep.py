import numpy as np
from scipy.stats import poisson
from catalog.model import Catalog
from model.kernels import productivity, omori_integral

def expected_events(catalog_train: Catalog, params: dict, t_start_test: float, t_end_test: float, area_km2: float) -> float:
    """
    Calculates the expected number of events (N_exp) during a testing window 
    given a training catalog and calibrated ETAS parameters.
    """
    df = catalog_train.data.sort_values('time_days')
    times = df['time_days'].values
    mags = df['magnitude'].values
    
    mu, k, c, p, alpha = params['mu'], params['k'], params['c'], params['p'], params['alpha']
    mc = params.get('mc', 2.0)
    
    T_test = t_end_test - t_start_test
    
    # 1. Background expected
    n_exp = mu * T_test * area_km2
    
    # 2. Triggered expected from past events
    for i in range(len(times)):
        t_i = times[i]
        
        # Calculate overlap of [t_i, infinity] with [t_start_test, t_end_test]
        int_start = max(0.0, t_start_test - t_i)
        int_end = t_end_test - t_i
        
        if int_end > 0:
            prod = productivity(mags[i], mc, k, alpha)
            temp_int = omori_integral(int_end, c, p) - omori_integral(int_start, c, p)
            n_exp += prod * temp_int
            
    return n_exp

def n_test(n_obs: int, n_exp: float):
    """
    CSEP N-test (Number test).
    """
    delta_1 = poisson.cdf(n_obs, n_exp)
    delta_2 = 1.0 - poisson.cdf(n_obs - 1, n_exp) if n_obs > 0 else 1.0
    
    return delta_1, delta_2
