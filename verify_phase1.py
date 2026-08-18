import pandas as pd
import os
from obspy.clients.fdsn import Client
from catalog.model import Catalog
from catalog.quakeml import parse_quakeml_to_df

def verify_sc_catalog(filepath="sc-catalog.txt"):
    print(f"--- 1. Testing Static {filepath} ---")
    
    # 1. Read the text file
    # skip the first two non-data lines, and use comment='#' to safely 
    # ignore both the column header row and the summary footer row at the bottom.
    raw_df = pd.read_csv(
        filepath, 
        sep=r'\s+', 
        skiprows=2,
        comment='#',
        names=['Date', 'Time', 'ET', 'GT', 'MAG', 'M', 'LAT', 'LON', 'DEPTH', 'Q', 'EVID', 'NPH', 'NGRM']
    )
    
    # 2. Map the SCEDC format to our strict Phase 1 schema
    mapped_df = pd.DataFrame()
    
    # Combine Date and Time strings and explicitly set the parsing format
    mapped_df['time'] = pd.to_datetime(
        raw_df['Date'] + ' ' + raw_df['Time'], 
        format='%Y/%m/%d %H:%M:%S.%f', 
        utc=True
    )
    
    # Calculate continuous time_days since the first event
    t0 = mapped_df['time'].min()
    mapped_df['time_days'] = (mapped_df['time'] - t0).dt.total_seconds() / (24 * 3600)
    
    # Map remaining physical parameters
    mapped_df['lon'] = raw_df['LON']
    mapped_df['lat'] = raw_df['LAT']
    mapped_df['depth'] = raw_df['DEPTH']
    mapped_df['magnitude'] = raw_df['MAG']
    mapped_df['magnitude-type'] = raw_df['M']
    mapped_df['source-agency'] = 'SCEDC'
    mapped_df['event-id'] = raw_df['EVID'].astype(str)
    
    # 3. Instantiate the Catalog
    sc_catalog = Catalog(mapped_df)
    print(f"Success: Loaded sc-catalog with {len(sc_catalog)} events.")
    
    # 4. Test CSV & Parquet Round-Trip
    sc_catalog.to_csv("sc_test.csv")
    sc_catalog.to_parquet("sc_test.parquet")
    
    csv_cat = Catalog.from_csv("sc_test.csv")
    parq_cat = Catalog.from_parquet("sc_test.parquet")
    
    assert len(sc_catalog) == len(csv_cat) == len(parq_cat), "sc-catalog Round-trip failed!"
    print("Success: sc-catalog CSV and Parquet round-trip survived intact.\n")


def verify_usgs_pull():
    print("--- 2. Testing Fresh USGS Pull ---")
    client = Client("USGS")
    
    # 1. Download a tiny, fresh catalog to keep the test fast
    print("Downloading recent earthquakes from USGS...")
    catalog_obspy = client.get_events(starttime="2024-01-01", endtime="2024-01-05", minmagnitude=4.5)
    
    # 2. Save it temporarily as QuakeML
    xml_path = "temp_usgs.xml"
    catalog_obspy.write(xml_path, format="QUAKEML")
    
    # 3. Parse it using your Phase 1 QuakeML parser
    df = parse_quakeml_to_df(xml_path)
    usgs_catalog = Catalog(df)
    print(f"Success: Loaded USGS Catalog with {len(usgs_catalog)} events.")
    
    # 4. Test CSV & Parquet Round-Trip
    usgs_catalog.to_csv("usgs_test.csv")
    usgs_catalog.to_parquet("usgs_test.parquet")
    
    csv_cat = Catalog.from_csv("usgs_test.csv")
    parq_cat = Catalog.from_parquet("usgs_test.parquet")
    
    assert len(usgs_catalog) == len(csv_cat) == len(parq_cat), "USGS Round-trip failed!"
    print("Success: USGS CSV and Parquet round-trip survived intact.\n")


if __name__ == "__main__":
    verify_sc_catalog("sc-catalog.txt")
    verify_usgs_pull()
    
    # Clean up temporary test files
    files_to_remove = ["temp_usgs.xml", "usgs_test.csv", "usgs_test.parquet", "sc_test.csv", "sc_test.parquet"]
    for file in files_to_remove:
        if os.path.exists(file):
            os.remove(file)
            
    print("========================================")
    print(" PHASE 1 IS OFFICIALLY DONE! ")
    print("========================================")