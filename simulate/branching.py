import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from catalog.model import Catalog

def simulate_etas(params: dict, t_start: float, t_end: float, mc: float = 2.0, b_val: float = 1.0) -> Catalog:
    """
    Simulates a synthetic ETAS catalog using a forward branching process.
    """
    mu, k, c, p, alpha = params['mu'], params['k'], params['c'], params['p'], params['alpha']
    
    T = t_end - t_start
    n_bg = np.random.poisson(mu * T)
    
    if n_bg == 0:
        return Catalog(pd.DataFrame())
        
    bg_times = np.random.uniform(t_start, t_end, n_bg)
    beta = b_val * np.log(10)
    bg_mags = np.random.exponential(1/beta, n_bg) + mc
    
    events = []
    for i in range(n_bg):
        events.append({
            'time_days': bg_times[i],
            'magnitude': bg_mags[i],
            'lon': np.random.uniform(0, 1),
            'lat': np.random.uniform(0, 1),
            'generation': 0
        })
        
    queue = list(events)
    
    while len(queue) > 0:
        parent = queue.pop(0)
        
        n_exp = k * np.exp(alpha * (parent['magnitude'] - mc))
        n_after = np.random.poisson(n_exp)
        
        if n_after == 0:
            continue
            
        U = np.random.rand(n_after)
        # Inverse transform for normalized Omori kernel
        dt = c * ( (1 - U)**(-1 / (p - 1)) - 1 )
        
        after_times = parent['time_days'] + dt
        valid = after_times <= t_end
        after_times = after_times[valid]
        n_after = len(after_times)
        
        if n_after == 0:
            continue
            
        after_mags = np.random.exponential(1/beta, n_after) + mc
        
        for i in range(n_after):
            child = {
                'time_days': after_times[i],
                'magnitude': after_mags[i],
                'lon': np.random.uniform(0, 1),
                'lat': np.random.uniform(0, 1),
                'generation': parent['generation'] + 1
            }
            events.append(child)
            queue.append(child)
            
    df = pd.DataFrame(events)
    df['time'] = [datetime(2000,1,1) + timedelta(days=t) for t in df['time_days']]
    df['depth'] = 10.0
    df['magnitude-type'] = 'ML'
    df['source-agency'] = 'SIM'
    df['event-id'] = [str(i) for i in range(len(df))]
    
    return Catalog(df)
