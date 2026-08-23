from typing import Tuple, Optional
from datetime import datetime, timedelta
from obspy.clients.fdsn import Client
import os
import pandas as pd
from catalog.model import Catalog
from catalog.quakeml import parse_quakeml_to_df

def fetch_fdsn(
    base_url: str,
    bbox: Tuple[float, float, float, float],
    time_range: Tuple[datetime, datetime],
    min_mag: Optional[float] = None
) -> Catalog:
    """
    Generic FDSN client covering standards-based nodes by base-URL swap.
    USGS 20,000-event cap is handled by automatic time-windowing recursion.
    """
    client = Client(base_url)
    min_lon, max_lon, min_lat, max_lat = bbox
    start_time, end_time = time_range
    
    try:
        catalog_obspy = client.get_events(
            starttime=start_time, endtime=end_time,
            minlatitude=min_lat, maxlatitude=max_lat,
            minlongitude=min_lon, maxlongitude=max_lon,
            minmagnitude=min_mag
        )
        
        # Save as QuakeML and parse
        temp_xml = f"temp_fdsn_fetch_{start_time.timestamp()}.xml"
        try:
            cat.write(temp_xml, format="QUAKEML")
            
            # Use our Phase 1 parser to enforce the Catalog schema
            df = parse_quakeml_to_df(temp_xml, start_time=start_time)
            return Catalog(df)
            
        finally:
            if os.path.exists(temp_xml):
                os.remove(temp_xml)
        
    except Exception as e:
        error_str = str(e).lower()
        if getattr(e, "status_code", None) == 204 or "204" in error_str or "no data" in error_str:
            print(f"[{base_url}] No events found (HTTP 204). Returning empty catalog.")
            return Catalog(pd.DataFrame(columns=Catalog.REQUIRED_COLUMNS))
        elif getattr(e, "status_code", None) == 400 or "400" in error_str or "request would result in too much data" in error_str:
            print(f"[{base_url}] Cap exceeded. Splitting time window: {start_time} to {end_time}")
            
            # Prevent infinite recursion if the window is too small (e.g., < 1 second)
            if (end_time - start_time).total_seconds() < 1:
                raise ValueError("Time window < 1s still exceeds max events.")
                
            # Split time window exactly in half
            mid_time = start_time + (end_time - start_time) / 2
            
            # Recursive calls
            cat1 = fetch_fdsn(base_url, bbox, (start_time, mid_time), min_mag)
            cat2 = fetch_fdsn(base_url, bbox, (mid_time, end_time), min_mag)
            
            # Combine the results
            merged_df = pd.concat([cat1.data, cat2.data], ignore_index=True)
            merged_df = merged_df.drop_duplicates(subset=['event-id'])
            if not merged_df.empty:
                merged_df = merged_df.sort_values('time').reset_index(drop=True)
                
            return Catalog(merged_df)
        else:
            print(f"[{base_url}] Failed to fetch data: {e}")
            raise e
