import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from catalog.model import Catalog

def plot_fmd(catalog: Catalog, ax=None, mc=None, b_value=None, a_value=None):
    if ax is None:
        fig, ax = plt.subplots(figsize=(8, 6))
    
    mags = catalog.data['magnitude'].dropna()
    if len(mags) == 0:
        return ax
        
    # Bin magnitudes
    bins = np.arange(mags.min(), mags.max() + 0.2, 0.1)
    hist, edges = np.histogram(mags, bins=bins)
    centers = edges[:-1] + 0.05
    
    # Cumulative histogram
    cum_hist = np.cumsum(hist[::-1])[::-1]
    
    ax.plot(centers, cum_hist, 's', color='black', label='Cumulative')
    ax.plot(centers, hist, '^', color='gray', label='Incremental')
    
    # Plot GR line if parameters provided (Calculated properly in Phase 4/5)
    if mc is not None and b_value is not None and a_value is not None:
        x = np.linspace(mc, mags.max(), 100)
        y = 10**(a_value - b_value * x)
        ax.plot(x, y, 'r-', label=f'b={b_value:.2f}, a={a_value:.2f}')
        ax.axvline(mc, color='red', linestyle='--', label=f'Mc={mc}')
        
    ax.set_yscale('log')
    ax.set_xlabel('Magnitude')
    ax.set_ylabel('Number of Earthquakes')
    ax.set_title('Frequency-Magnitude Distribution')
    ax.legend()
    ax.grid(True, which="both", ls="--", alpha=0.5)
    
    return ax
