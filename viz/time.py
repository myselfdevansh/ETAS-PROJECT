import matplotlib.pyplot as plt
import pandas as pd
from catalog.model import Catalog

def plot_time_magnitude(catalog: Catalog, ax=None):
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 4))
        
    df = catalog.data
    if len(df) == 0:
        return ax
        
    # Stem plot equivalent (using vlines for performance on large catalogs)
    ax.vlines(df['time'], ymin=df['magnitude'].min(), ymax=df['magnitude'], 
              color='gray', alpha=0.5, linewidth=0.5)
    ax.scatter(df['time'], df['magnitude'], s=df['magnitude']**2, color='blue', alpha=0.6)
    
    ax.set_xlabel('Time')
    ax.set_ylabel('Magnitude')
    ax.set_title('Time-Magnitude View')
    ax.grid(True, alpha=0.3)
    return ax

def plot_cumulative_count(catalog: Catalog, ax=None):
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 4))
        
    df = catalog.data.sort_values('time')
    if len(df) == 0:
        return ax
        
    ax.step(df['time'], range(1, len(df) + 1), color='black')
    ax.set_xlabel('Time')
    ax.set_ylabel('Cumulative Event Count')
    ax.set_title('Cumulative Seismicity')
    ax.grid(True, alpha=0.3)
    return ax
