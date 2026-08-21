from typing import Tuple, Optional
from datetime import datetime
import obspy
import os
import requests
import pandas as pd
from catalog.model import Catalog

def get_events(
    bbox: Tuple[float, float, float, float],
    time_range: Tuple[datetime, datetime],
    min_mag: Optional[float] = None
) -> Catalog:
    """
    Global CMT: downloads recent .ndk file, parses via ObsPy for moment tensors.
    """
    # LDEO GCMT quickcmt URL (example for recent events)
    ndk_url = "https://www.ldeo.columbia.edu/~gcmt/projects/CMT/catalog/NEW_MONTHLY/2023/jan23.ndk"
    
    print(f"Downloading GCMT NDK from {ndk_url}...")
    response = requests.get(ndk_url)
    response.raise_for_status()
    
    temp_ndk = "temp_gcmt.ndk"
    with open(temp_ndk, "wb") as f:
        f.write(response.content)
        
    try:
        # ObsPy natively reads NDK format
        obspy_cat = obspy.read_events(temp_ndk, format="NDK")
        
        flat_events = []
        for event in obspy_cat:
            origin = event.preferred_origin() or event.origins[0]
            magnitude = event.preferred_magnitude() or event.magnitudes[0]
            
            flat_events.append({
                'event-id': str(event.resource_id),
                'time': pd.to_datetime(origin.time.datetime, utc=True),
                'lon': origin.longitude,
                'lat': origin.latitude,
                'depth': origin.depth / 1000.0 if origin.depth else None,
                'magnitude': magnitude.mag,
                'magnitude-type': magnitude.magnitude_type,
                'source-agency': "GCMT"
            })
            
        df = pd.DataFrame(flat_events)
        
        # Filter bbox and time
        min_lon, max_lon, min_lat, max_lat = bbox
        start_time, end_time = time_range
        start_time, end_time = pd.to_datetime(start_time, utc=True), pd.to_datetime(end_time, utc=True)
        
        df = df[
            (df['time'] >= start_time) & (df['time'] <= end_time) &
            (df['lon'] >= min_lon) & (df['lon'] <= max_lon) &
            (df['lat'] >= min_lat) & (df['lat'] <= max_lat)
        ]
        
        if min_mag is not None:
            df = df[df['magnitude'] >= min_mag]
            
        if not df.empty:
            df = df.sort_values('time').reset_index(drop=True)
            df['time_days'] = (df['time'] - df['time'].iloc[0]).dt.total_seconds() / (24 * 3600)
        else:
            df = pd.DataFrame(columns=Catalog.REQUIRED_COLUMNS)
            
        return Catalog(df)
        
    finally:
        if os.path.exists(temp_ndk):
            os.remove(temp_ndk)
