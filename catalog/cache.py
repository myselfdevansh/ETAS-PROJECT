import os
import hashlib
import pandas as pd
from typing import Callable

# Define the cache directory path in your home folder
CACHE_DIR = os.path.expanduser("~/.etas_cache")

def _generate_cache_filename(source: str, start_time: str, end_time: str, 
                             min_lon: float, max_lon: float, 
                             min_lat: float, max_lat: float, min_mag: float) -> str:
    """
    Creates a unique, reproducible filename based on the exact query parameters.
    """
    # Combine all parameters into a single string
    query_string = f"{source}_{start_time}_{end_time}_{min_lon}_{max_lon}_{min_lat}_{max_lat}_{min_mag}"
    
    # Hash the string using MD5 to create a safe, consistent filename
    query_hash = hashlib.md5(query_string.encode('utf-8')).hexdigest()
    
    # Return the full file path ending in .parquet
    return os.path.join(CACHE_DIR, f"{query_hash}.parquet")

def fetch_with_cache(download_function: Callable, source: str, start_time: str, end_time: str, 
                     min_lon: float, max_lon: float, min_lat: float, max_lat: float, min_mag: float) -> pd.DataFrame:
    """
    Acts as a middleman. Checks the cache for the requested data. 
    If present, loads it. If not, executes the download function and saves the result.
    """
    # 1. Ensure the hidden cache directory exists on the hard drive
    os.makedirs(CACHE_DIR, exist_ok=True)
    
    # 2. Determine what the filename for this specific query would be
    cache_filepath = _generate_cache_filename(
        source, start_time, end_time, min_lon, max_lon, min_lat, max_lat, min_mag
    )
    
    # 3. If the file already exists, load it directly from the local disk
    if os.path.exists(cache_filepath):
        print(f"Success: Loading cached data for {source} from {cache_filepath}")
        return pd.read_parquet(cache_filepath)
        
    # 4. If the file does not exist, we must hit the network
    print(f"Data not found in cache. Initiating network download from {source}...")
    
    # Execute the actual network download (e.g., pulling from USGS ComCat)
    raw_dataframe = download_function(
        start_time, end_time, min_lon, max_lon, min_lat, max_lat, min_mag
    )
    
    # 5. Save the newly downloaded data to the cache so we never have to download it again
    if not raw_dataframe.empty:
        raw_dataframe.to_parquet(cache_filepath, index=False)
        print(f"Data successfully downloaded and cached to {cache_filepath}")
    
    return raw_dataframe