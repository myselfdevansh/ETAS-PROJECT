import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from catalog.model import Catalog
from viz.fmd import plot_fmd
from viz.maps import plot_epicenter_map
from viz.time import plot_time_magnitude, plot_cumulative_count
from viz.interevent import plot_interevent_time, plot_cumulative_moment
import os

def create_eda_dashboard(catalog: Catalog, region_name: str):
    """
    Generates the multi-panel EDA figure for a Catalog.
    DONE WHEN: One function call produces a labeled multi-panel EDA figure.
    """
    fig = plt.figure(figsize=(20, 15))
    
    # Grid layout mapping
    ax_map = plt.subplot(2, 3, (1, 2), projection=ccrs.PlateCarree())
    ax_fmd = plt.subplot(2, 3, 3)
    
    ax_time = plt.subplot(4, 2, 5)
    ax_cum = plt.subplot(4, 2, 7)
    
    ax_inter = plt.subplot(4, 2, 6)
    ax_moment = plt.subplot(4, 2, 8)
    
    # 1. Plot Epicenter Map
    plot_epicenter_map(catalog, ax=ax_map)
    
    # 2. Plot Frequency-Magnitude Distribution
    plot_fmd(catalog, ax=ax_fmd)
    
    # 3. Plot Time-Magnitude & Cumulative Count
    plot_time_magnitude(catalog, ax=ax_time)
    plot_cumulative_count(catalog, ax=ax_cum)
    
    # 4. Plot Inter-event Time & Cumulative Moment Release
    plot_interevent_time(catalog, ax=ax_inter)
    plot_cumulative_moment(catalog, ax=ax_moment)
    
    plt.suptitle(f'Exploratory Data Analysis (EDA): {region_name}', fontsize=24)
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    
    os.makedirs('docs/figures', exist_ok=True)
    filepath = f'docs/figures/eda_dashboard_{region_name.lower().replace(" ", "_")}.png'
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    print(f"EDA Dashboard saved successfully to: {filepath}")
    
    return fig
