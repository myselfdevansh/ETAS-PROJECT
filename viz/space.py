import matplotlib.pyplot as plt
from catalog.model import Catalog

def plot_depth_cross_section(catalog: Catalog, ax=None):
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 4))
        
    df = catalog.data
    if len(df) == 0:
        return ax
        
    ax.scatter(df['lon'], df['depth'], c='gray', alpha=0.5, s=df['magnitude']**2)
    
    ax.set_ylim(df['depth'].max() + 10, -5) # Invert y-axis for depth
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Depth (km)')
    ax.set_title('East-West Depth Cross Section')
    ax.grid(True, alpha=0.3)
    return ax
