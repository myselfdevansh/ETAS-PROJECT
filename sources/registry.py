import argparse
from datetime import datetime
import functools
import pandas as pd

# Load Cache function from Phase 1
from catalog.cache import fetch_with_cache
from catalog.model import Catalog

# Import sources
import sources.comcat
import sources.isc
import sources.geonet
import sources.gcmt
import sources.afad
import sources.scrape.csn_chile
import sources.scrape.koeri
from sources.fdsn import fetch_fdsn

# A wrapper to register generic FDSN endpoints directly
def make_fdsn_fetcher(base_url):
    return functools.partial(fetch_fdsn, base_url)

# The mapping (6 APIs + 2 Scrapers)
REGISTRY = {
    'california': sources.comcat.get_events,
    'global_isc': sources.isc.get_events,
    'global_gcmt': sources.gcmt.get_events,
    'new_zealand': sources.geonet.get_events,
    'europe_emsc': make_fdsn_fetcher("EMSC"),
    'turkiye_afad': sources.afad.get_events,
    'chile_scrape': sources.scrape.csn_chile.get_events,
    'turkiye_koeri_scrape': sources.scrape.koeri.get_events,
}

def cached_fetch(region: str, fetcher, bbox, time_range, min_mag) -> Catalog:
    """
    Adapter to route requests through Phase 1's fetch_with_cache.
    """
    start_time, end_time = time_range
    min_lon, max_lon, min_lat, max_lat = bbox
    min_mag = min_mag or 0.0
    
    # We create a dummy callable for fetch_with_cache that ignores the 7 positional arguments
    # because it passes them when calling it, but our fetcher expects bbox and time_range.
    def download_function(st, et, minlon, maxlon, minlat, maxlat, minm):
        # We parse the strings back to datetime objects since cache passes them
        try:
            # Depending on how the user uses cache.py it might pass strings. 
            # In our CLI, we'll ensure they are datetimes inside our download_function.
            st_dt = datetime.fromisoformat(st) if isinstance(st, str) else st
            et_dt = datetime.fromisoformat(et) if isinstance(et, str) else et
        except:
            st_dt, et_dt = start_time, end_time
            
        catalog = fetcher((minlon, maxlon, minlat, maxlat), (st_dt, et_dt), minm)
        return catalog.data
    
    # Call fetch_with_cache
    df = fetch_with_cache(
        download_function=download_function,
        source=region,
        start_time=start_time.isoformat(),
        end_time=end_time.isoformat(),
        min_lon=min_lon, max_lon=max_lon,
        min_lat=min_lat, max_lat=max_lat,
        min_mag=min_mag
    )
    
    return Catalog(df)


def main():
    parser = argparse.ArgumentParser(description="ETAS Catalog Source Registry")
    parser.add_argument("--region", type=str, required=True, help="Region to fetch catalog for")
    parser.add_argument("--from_date", type=str, required=True, help="Start date (YYYY-MM-DD)")
    parser.add_argument("--to_date", type=str, required=True, help="End date (YYYY-MM-DD)")
    parser.add_argument("--min-mag", type=float, default=2.5, help="Minimum magnitude")
    
    args = parser.parse_args()
    
    if args.region not in REGISTRY:
        print(f"Region {args.region} not supported yet. Supported: {list(REGISTRY.keys())}")
        return
        
    start_time = datetime.strptime(args.from_date, "%Y-%m-%d")
    end_time = datetime.strptime(args.to_date, "%Y-%m-%d")
    
    # Global dummy bbox for demonstration
    bbox = (-180, 180, -90, 90)
    
    fetcher = REGISTRY[args.region]
    print(f"Fetching {args.region} catalog from {start_time} to {end_time}...")
    
    # Pass through the caching layer
    catalog = cached_fetch(args.region, fetcher, bbox, (start_time, end_time), args.min_mag)
    
    print(f"Success! Fetched {len(catalog)} events.")

if __name__ == '__main__':
    main()
