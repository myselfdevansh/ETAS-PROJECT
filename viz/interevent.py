import numpy as np
import matplotlib.pyplot as plt
from catalog.model import Catalog

def plot_interevent_time(catalog: Catalog, ax=None):
    if ax is None:
        fig, ax = plt.subplots(figsize=(8, 5))
        
    df = catalog.data.sort_values('time')
    if len(df) < 2:
        return ax
        
    # Calculate time difference in days
    dt = df['time'].diff().dt.total_seconds().dropna() / (24 * 3600)
    dt = dt[dt > 0] # Avoid log(0) for coincident events
    
    bins = np.logspace(np.log10(dt.min()), np.log10(dt.max()), 50)
    ax.hist(dt, bins=bins, color='steelblue', edgecolor='black', alpha=0.7)
    
    ax.set_xscale('log')
    ax.set_xlabel('Inter-event Time (days)')
    ax.set_ylabel('Count')
    ax.set_title('Inter-event Time Distribution')
    ax.grid(True, alpha=0.3)
    return ax

def plot_cumulative_moment(catalog: Catalog, ax=None):
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 4))
        
    df = catalog.data.sort_values('time')
    if len(df) == 0:
        return ax
        
    # M0 = 10^(1.5 * Mw + 9.1)
    moment = 10**(1.5 * df['magnitude'] + 9.1)
    cum_moment = np.cumsum(moment)
    
    ax.step(df['time'], cum_moment, color='darkred')
    ax.set_yscale('log')
    ax.set_xlabel('Time')
    ax.set_ylabel('Cumulative Moment (N m)')
    ax.set_title('Cumulative Moment Release')
    ax.grid(True, alpha=0.3)
    return ax
