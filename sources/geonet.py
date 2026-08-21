from typing import Tuple, Optional
from datetime import datetime
from catalog.model import Catalog

def get_events(
    bbox: Tuple[float, float, float, float],
    time_range: Tuple[datetime, datetime],
    min_mag: Optional[float] = None
) -> Catalog:
    """New Zealand GeoNet QuakeSearch/WFS CSV."""
    # Can also just use FDSN for GeoNet for now
    from sources.fdsn import fetch_fdsn
    return fetch_fdsn("GEONET", bbox, time_range, min_mag)
