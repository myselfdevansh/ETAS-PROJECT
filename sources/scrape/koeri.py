from typing import Tuple, Optional
from datetime import datetime
import pandas as pd
import requests
from catalog.model import Catalog
import io

def get_events(
    bbox: Tuple[float, float, float, float],
    time_range: Tuple[datetime, datetime],
    min_mag: Optional[float] = None
) -> Catalog:
    """
    Türkiye/KOERI: scrape HTML/<pre> text listings.
    """
    print("Scraping KOERI HTML <pre> block...")
    url = "http://www.koeri.boun.edu.tr/scripts/lst9.asp"
    r = requests.get(url)
    # the page is in windows-1254 encoding
    r.encoding = 'windows-1254'
    
    # Extract the <pre> block
    import re
    match = re.search(r'<pre>(.*?)</pre>', r.text, flags=re.DOTALL | re.IGNORECASE)
    if not match:
        return Catalog(pd.DataFrame(columns=Catalog.REQUIRED_COLUMNS))
        
    pre_text = match.group(1)
    
    # Find the data start (Line 7 is dashes)
    lines = pre_text.split('\n')
    data_lines = []
    start_collecting = False
    for line in lines:
        if line.startswith('----------'):
            start_collecting = True
            continue
        if start_collecting and line.strip():
            # End of valid block might occur
            if "Son 500 deprem listelenmi" in line: continue
            data_lines.append(line)
            
    # Process into dataframe. Columns: Date, Time, Lat, Lon, Depth, MD, ML, Mw, Place
    df_rows = []
    for line in data_lines:
        parts = line.split()
        if len(parts) >= 9:
            try:
                date = parts[0]
                time_str = parts[1]
                lat = float(parts[2])
                lon = float(parts[3])
                depth = float(parts[4])
                # We use ML if valid, else MD or Mw
                ml = float(parts[6]) if parts[6] != '-.-' else 0.0
                if parts[6] != '-.-':
                    mag = ml
                    mtype = 'ML'
                elif parts[7] != '-.-':
                    mag = float(parts[7])
                    mtype = 'Mw'
                elif parts[5] != '-.-':
                    mag = float(parts[5])
                    mtype = 'MD'
                else:
                    mag = 0.0
                    mtype = 'Unknown'
                    
                df_rows.append({
                    'time': pd.to_datetime(f"{date.replace('.','-')}T{time_str}", utc=True),
                    'lat': lat,
                    'lon': lon,
                    'depth': depth,
                    'magnitude': mag,
                    'magnitude-type': mtype,
                    'source-agency': 'KOERI',
                    'event-id': f"KOERI_{date}_{time_str}"
                })
            except Exception as e:
                continue
                
    df = pd.DataFrame(df_rows)
    
    if not df.empty:
        # Filter bbox and time
        min_lon, max_lon, min_lat, max_lat = bbox
        start_time, end_time = time_range
        start_time = pd.to_datetime(start_time, utc=True)
        end_time = pd.to_datetime(end_time, utc=True)
        
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
