import pandas as pd
import obspy

def parse_quakeml_to_df(file_path: str) -> pd.DataFrame:
    """
    Reads a QuakeML file and flattens the nested event data 
    into a structured Pandas DataFrame.
from datetime import timezone

def parse_quakeml_to_df(file_path: str, start_time=None) -> pd.DataFrame:
    """
    Reads a QuakeML XML file and flattens it into a Pandas DataFrame.
    """
    catalog = obspy.read_events(file_path, format="QUAKEML")
    
    events_data = []
    
    for event in catalog:
        # Get preferred origin (or first available)
        origin = event.preferred_origin() or (event.origins[0] if event.origins else None)
        
        # Get preferred magnitude (or first available)
        mag = event.preferred_magnitude() or (event.magnitudes[0] if event.magnitudes else None)
        
        if origin and mag:
            event_id = str(event.resource_id)
            time = origin.time.datetime.replace(tzinfo=timezone.utc)
            lon = origin.longitude
            lat = origin.latitude
            depth = origin.depth / 1000.0 if origin.depth is not None else None # Convert m to km
            magnitude = mag.mag
            mag_type = mag.magnitude_type
            
            events_data.append({
                'event-id': event_id,
                'time': time,
                'lon': lon,
                'lat': lat,
                'depth': depth,
                'magnitude': magnitude,
                'mag_type': mag_type
            })
            
    catalog_df = pd.DataFrame(events_data)
    
    if not catalog_df.empty:
        catalog_df = catalog_df.sort_values('time').reset_index(drop=True)
        # Calculate time in days since the start of the catalog
        t0 = pd.to_datetime(start_time, utc=True) if start_time else catalog_df['time'].iloc[0]
        catalog_df['time_days'] = (catalog_df['time'] - t0).dt.total_seconds() / (24 * 3600)
        
    return catalog_df