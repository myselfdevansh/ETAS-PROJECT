from typing import Tuple, Optional
from datetime import datetime
import requests
import pandas as pd
from catalog.model import Catalog

def get_events(
    bbox: Tuple[float, float, float, float],
    time_range: Tuple[datetime, datetime],
    min_mag: Optional[float] = None
) -> Catalog:
    """Türkiye AFAD custom REST/JSON API."""
    url = "https://deprem.afad.gov.tr/apiv2/event/filter"
    
    min_lon, max_lon, min_lat, max_lat = bbox
    start_time, end_time = time_range
    
    params = {
        "start": start_time.strftime("%Y-%m-%d %H:%M:%S"),
        "end": end_time.strftime("%Y-%m-%d %H:%M:%S"),
        "minlat": min_lat,
        "maxlat": max_lat,
        "minlon": min_lon,
        "maxlon": max_lon
    }
    if min_mag is not None:
        params["minmag"] = min_mag
        
    response = requests.get(url, params=params)
    response.raise_for_status()
    
    data = response.json()
    if not data:
        return Catalog(pd.DataFrame(columns=Catalog.REQUIRED_COLUMNS))
        
    df = pd.DataFrame(data)
    
    # Map AFAD JSON to our standard
    mapped_df = pd.DataFrame()
    mapped_df['time'] = pd.to_datetime(df['date'], utc=True)
    mapped_df['lon'] = df['longitude'].astype(float)
    mapped_df['lat'] = df['latitude'].astype(float)
    mapped_df['depth'] = df['depth'].astype(float)
    mapped_df['magnitude'] = df['magnitude'].astype(float)
    mapped_df['magnitude-type'] = df['type']
    mapped_df['source-agency'] = 'AFAD'
    mapped_df['event-id'] = df['eventID'].astype(str)
    
    mapped_df = mapped_df.sort_values('time').reset_index(drop=True)
    mapped_df['time_days'] = (mapped_df['time'] - mapped_df['time'].iloc[0]).dt.total_seconds() / (24 * 3600)
    
    return Catalog(mapped_df)
