import numpy as np
import pandas as pd
from catalog.model import Catalog
from calibrate.em import e_step

def stochastic_decluster(catalog: Catalog, params: dict, t_start: float, t_end: float) -> Catalog:
    """
    Performs stochastic declustering to isolate background seismicity.
    Uses the E-step branching probabilities.
    """
    # 1. Compute branching probabilities
    P = e_step(catalog, params, t_start, t_end)
    
    df = catalog.data.sort_values('time_days').reset_index(drop=True)
    
    # 2. Extract background probabilities (diagonal of P)
    p_bg = np.diag(P)
    
    # 3. Stochastic selection (Event j is background if U < p_bg[j])
    U = np.random.rand(len(df))
    is_background = U < p_bg
    
    bg_df = df[is_background].copy()
    return Catalog(bg_df)
