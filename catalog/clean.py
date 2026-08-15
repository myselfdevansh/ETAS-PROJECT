import pandas as pd

# ---------------------------------------------------------
# Sorting and Deduplication
# ---------------------------------------------------------

def sort_by_time(catalog_df: pd.DataFrame) -> pd.DataFrame:
    """
    Sorts the catalog chronologically based on the UTC time column.
    """
    return catalog_df.sort_values(by='time').reset_index(drop=True)

def remove_duplicates(catalog_df: pd.DataFrame) -> pd.DataFrame:
    """
    Removes duplicate events. 
    First checks for duplicate unique IDs, then checks for events 
    that share the exact same time, latitude, and longitude.
    """
    # 1. Drop identical event IDs
    df_cleaned = catalog_df.drop_duplicates(subset=['event-id'])
    
    # 2. Drop identical physical events (same time and location)
    df_cleaned = df_cleaned.drop_duplicates(subset=['time', 'lat', 'lon'])
    
    return df_cleaned.reset_index(drop=True)

# ---------------------------------------------------------
# Core Filters
# ---------------------------------------------------------

def filter_spatial(catalog_df: pd.DataFrame, min_lon: float, max_lon: float, min_lat: float, max_lat: float) -> pd.DataFrame:
    """
    Crops the catalog to a specific spatial bounding box.
    """
    mask = (
        (catalog_df['lon'] >= min_lon) & 
        (catalog_df['lon'] <= max_lon) & 
        (catalog_df['lat'] >= min_lat) & 
        (catalog_df['lat'] <= max_lat)
    )
    return catalog_df[mask].reset_index(drop=True)

def filter_temporal(catalog_df: pd.DataFrame, start_time: str, end_time: str) -> pd.DataFrame:
    """
    Filters events to strictly fall within a specific time window.
    start_time and end_time should be strings parsable by pandas (e.g., '2010-01-01').
    """
    start_dt = pd.to_datetime(start_time, utc=True)
    end_dt = pd.to_datetime(end_time, utc=True)
    
    mask = (catalog_df['time'] >= start_dt) & (catalog_df['time'] <= end_dt)
    return catalog_df[mask].reset_index(drop=True)

def filter_magnitude(catalog_df: pd.DataFrame, min_mag: float) -> pd.DataFrame:
    """
    Filters events strictly above or equal to a minimum magnitude threshold.
    """
    return catalog_df[catalog_df['magnitude'] >= min_mag].reset_index(drop=True)

# ---------------------------------------------------------
# Magnitude Homogenization Stubs
# ---------------------------------------------------------

def homogenize_ml_to_mw(catalog_df: pd.DataFrame) -> pd.DataFrame:
    """
    STUB: Convert Local Magnitude (ML) to Moment Magnitude (Mw).
    To be implemented using regional empirical conversion relations.
    """
    pass

def homogenize_ms_to_mw(catalog_df: pd.DataFrame) -> pd.DataFrame:
    """
    STUB: Convert Surface Wave Magnitude (Ms) to Moment Magnitude (Mw).
    To be implemented using regional empirical conversion relations.
    """
    pass

def homogenize_magnitudes(catalog_df: pd.DataFrame) -> pd.DataFrame:
    """
    STUB: Master function to harmonize all magnitude types in the catalog to Mw.
    This function will route rows to the correct specific conversion function above.
    """
    pass