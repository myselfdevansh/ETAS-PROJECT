import numpy as np
import pandas as pd
from catalog.model import Catalog
from quality.mc import calc_maxc, calc_gft, calc_mbs, calc_emr, calc_mbass
from scipy.spatial import cKDTree

def calculate_mc_grid(
    catalog: Catalog,
    method: str = 'MAXC',
    grid_spacing: float = 0.5,
    n_events: int = 250
) -> pd.DataFrame:
    """
    Calculates spatial variation of Mc across a geographic grid using 
    constant-N nearest-neighbor sampling.
    
    Args:
        catalog: The full earthquake Catalog
        method: Which Mc estimation method to use ('MAXC', 'GFT', 'MBS', 'EMR', 'MBASS')
        grid_spacing: Spacing of the grid in degrees
        n_events: Number of nearest neighbors to sample at each grid node
        
    Returns:
        pd.DataFrame with columns ['lon', 'lat', 'mc']
    """
    df = catalog.data.dropna(subset=['lon', 'lat', 'magnitude']).copy()
    
    # Create the grid
    min_lon, max_lon = df['lon'].min(), df['lon'].max()
    min_lat, max_lat = df['lat'].min(), df['lat'].max()
    
    lons = np.arange(min_lon, max_lon, grid_spacing)
    lats = np.arange(min_lat, max_lat, grid_spacing)
    lon_grid, lat_grid = np.meshgrid(lons, lats)
    
    grid_points = np.c_[lon_grid.ravel(), lat_grid.ravel()]
    
    # KDTree for fast spatial nearest neighbor searches
    coords = df[['lon', 'lat']].values
    tree = cKDTree(coords)
    
    results = []
    
    # Map string names to the actual functions we wrote in mc.py
    mc_funcs = {
        'MAXC': calc_maxc,
        'GFT': calc_gft,
        'MBS': calc_mbs,
        'EMR': calc_emr,
        'MBASS': calc_mbass
    }
    mc_func = mc_funcs.get(method.upper(), calc_maxc)
    
    # For each grid point, find the n_events nearest earthquakes
    for point in grid_points:
        # Get indices of the N nearest earthquakes to this grid node
        dist, indices = tree.query(point, k=min(n_events, len(df)))
        
        # If there are not enough events globally, break out
        if isinstance(indices, int) or len(indices) < 50:
            results.append(np.nan)
            continue
            
        # Create a sub-catalog of just those local events
        sub_df = df.iloc[indices]
        sub_catalog = Catalog(sub_df)
        
        # Calculate Mc for this local spatial patch
        local_mc = mc_func(sub_catalog)
        results.append(local_mc)
        
    # Return as a DataFrame for easy geographic plotting later
    return pd.DataFrame({
        'lon': grid_points[:, 0],
        'lat': grid_points[:, 1],
        'mc': results
    })
