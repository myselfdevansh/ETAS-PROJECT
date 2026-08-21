from typing import Tuple, Optional
from datetime import datetime
from catalog.model import Catalog

def get_events(
    bbox: Tuple[float, float, float, float],
    time_range: Tuple[datetime, datetime],
    min_mag: Optional[float] = None
) -> Catalog:
    """Base interface for all catalog downloaders."""
    raise NotImplementedError("Interface method, implement in specific module.")
