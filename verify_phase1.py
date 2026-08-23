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
    try:
        print("1. Verifying Southern California Catalog parser...")
        
        # 1. Read raw file
        raw_df = pd.read_csv(filepath, sep=r'\s+', comment='#')
        
        # 2. Map columns to ETAS schema
        mapped_df = pd.DataFrame()
        mapped_df['time'] = pd.to_datetime(raw_df['#YYY/MM/DD'] + ' ' + raw_df['HH:mm:SS.ss'])
        mapped_df['lat'] = raw_df['LAT']
        mapped_df['lon'] = raw_df['LON']
        mapped_df['depth'] = raw_df['DEPTH']
        mapped_df['magnitude'] = raw_df['MAG']
        mapped_df['mag_type'] = 'ML'  # Usually ML for SC
        mapped_df['event-id'] = raw_df['EVID'].astype(str)
        
        mapped_df = mapped_df.dropna(subset=['time'])
        
        # 3. Instantiate the Catalog
        sc_catalog = Catalog(mapped_df)
        
        print(f"Loaded {len(sc_catalog)} events.")
        
        # 4. Test Parquet & CSV Round-Trip
        sc_catalog.to_parquet("sc_test.parquet")
        sc_catalog.to_csv("sc_test.csv")
        
        parq_cat = Catalog.from_parquet("sc_test.parquet")
        csv_cat = Catalog.from_csv("sc_test.csv")
        
        assert len(sc_catalog) == 9417, f"Expected 9417, got {len(sc_catalog)}"
        assert_frame_equal(sc_catalog.data, csv_cat.data, check_dtype=False)
        assert_frame_equal(sc_catalog.data, parq_cat.data, check_dtype=False)
        print("Success: sc-catalog CSV and Parquet round-trip survived intact.\n")
    finally:
        for f in ["sc_test.csv", "sc_test.parquet"]:
            if os.path.exists(f): os.remove(f)

def verify_usgs_pull():
    try:
        print("2. Verifying USGS FDSN XML downloading and parsing...")
        from obspy.clients.fdsn import Client
        
        # 1. Download a tiny catalog
        client = Client("USGS")
        t1 = pd.to_datetime("2023-01-01T00:00:00", utc=True)
        t2 = pd.to_datetime("2023-01-02T00:00:00", utc=True)
        
        cat = client.get_events(starttime=t1, endtime=t2, minmagnitude=4.5)
        cat.write("temp_usgs.xml", format="QUAKEML")
        
        # 2. Parse using our custom QuakeML flattener
        from catalog.quakeml import parse_quakeml_to_df
        df = parse_quakeml_to_df("temp_usgs.xml")
        
        usgs_catalog = Catalog(df)
        print(f"Loaded {len(usgs_catalog)} events from USGS.")
        
        # 3. Test Parquet & CSV Round-Trip
        usgs_catalog.to_parquet("usgs_test.parquet")
        usgs_catalog.to_csv("usgs_test.csv")
        
        parq_cat = Catalog.from_parquet("usgs_test.parquet")
        csv_cat = Catalog.from_csv("usgs_test.csv")
        
        assert_frame_equal(usgs_catalog.data, csv_cat.data, check_dtype=False)
        assert_frame_equal(usgs_catalog.data, parq_cat.data, check_dtype=False)
        print("Success: USGS CSV and Parquet round-trip survived intact.\n")
    finally:
        for f in ["temp_usgs.xml", "usgs_test.csv", "usgs_test.parquet"]:
            if os.path.exists(f): os.remove(f)

if __name__ == "__main__":
    verify_sc_catalog()
    verify_usgs_pull()
    print("ALL PHASE 1 VERIFICATIONS PASSED!")
    print("========================================")
    print(" PHASE 1 IS OFFICIALLY DONE! ")
    print("========================================")