import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from catalog.model import Catalog

def plot_epicenter_map(catalog: Catalog, ax=None):
    if ax is None:
        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
        
    ax.add_feature(cfeature.LAND, facecolor='lightgray')
    ax.add_feature(cfeature.OCEAN, facecolor='azure')
    ax.add_feature(cfeature.COASTLINE)
    ax.add_feature(cfeature.BORDERS, linestyle=':')
    
    df = catalog.data
    if len(df) == 0:
        return ax
        
    # Scale marker size by magnitude (exponential scaling makes it visible)
    sizes = 2 ** df['magnitude']
    
    scatter = ax.scatter(
        df['lon'], df['lat'],
        s=sizes, c=df['depth'], cmap='viridis_r',
        alpha=0.7, edgecolors='k', linewidth=0.5,
        transform=ccrs.PlateCarree()
    )
    
    # Add colorbar for depth
    plt.colorbar(scatter, ax=ax, label='Depth (km)', shrink=0.7)
    
    # Add gridlines
    gl = ax.gridlines(draw_labels=True, linestyle='--', alpha=0.5)
    gl.top_labels = False
    gl.right_labels = False
    
    ax.set_title('Epicenter Map')
    return ax
