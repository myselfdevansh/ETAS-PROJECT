import pandas as pd
import obspy

def parse_quakeml_to_df(file_path: str) -> pd.DataFrame:
    """
    Reads a QuakeML file and flattens the nested event data 
    into a structured Pandas DataFrame.
    """
    # 1. Let ObsPy parse the complex XML file into an ObsPy Catalog object
    obspy_catalog = obspy.read_events(file_path)
    
    flat_events = []
    
    # 2. Loop through every earthquake event in the file
    for event in obspy_catalog:
        
        # Earthquakes often have multiple location/size estimates. 
        # We grab the 'preferred' one, or default to the first one available.
        origin = event.preferred_origin() or event.origins[0]
        magnitude = event.preferred_magnitude() or event.magnitudes[0]
        
        # 3. Pluck only the relevant physical parameters
        event_data = {
            'event-id': str(event.resource_id),
            'time': origin.time.datetime,  # Converts ObsPy UTCDateTime to standard Python datetime
            'lon': origin.longitude,
            'lat': origin.latitude,
            'depth': origin.depth / 1000.0 if origin.depth else None,  # Convert meters to km
            'magnitude': magnitude.mag,
            'magnitude-type': magnitude.magnitude_type,
            'source-agency': origin.creation_info.agency_id if origin.creation_info else "Unknown"
        }
        
        # Add this flattened dictionary to our list
        flat_events.append(event_data)
        
    # 4. Convert the list of flat dictionaries into a Pandas DataFrame
    catalog_df = pd.DataFrame(flat_events)
    
    # 5. Calculate continuous 'time_days' since the origin (required for ETAS)
    if not catalog_df.empty:
        # Sort chronologically just in case the QuakeML was out of order
        catalog_df = catalog_df.sort_values('time').reset_index(drop=True)
        
        # Calculate days elapsed since the very first event in the catalog
        t0 = catalog_df['time'].iloc[0]
        catalog_df['time_days'] = (catalog_df['time'] - t0).dt.total_seconds() / (24 * 3600)

    return catalog_df