from sources.fdsn import fetch_fdsn
from typing import Tuple, Optional
from datetime import datetime
from catalog.model import Catalog

def get_events(
    bbox: Tuple[float, float, float, float],
    time_range: Tuple[datetime, datetime],
    min_mag: Optional[float] = None
) -> Catalog:
    """ISC Event Catalogue (CSV/QuakeML) plus ISC-GEM."""
    return fetch_fdsn("ISC", bbox, time_range, min_mag)
