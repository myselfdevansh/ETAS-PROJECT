import pandas as pd
import os

class Catalog:
    """
    A pandas-backed data model for earthquake catalogs.
    Strictly enforces the required schema and provides I/O operations.
    """
    
    # The strict schema required by the ETAS project
    REQUIRED_COLUMNS = [
        'time', 
        'time_days', 
        'lon', 
        'lat', 
        'depth', 
        'magnitude', 
        'magnitude-type', 
        'source-agency', 
        'event-id'
    ]

    def __init__(self, data: pd.DataFrame):
        """
        Initializes the Catalog object and validates the incoming DataFrame.
        """
        self._validate(data)
        
        # Store a copy to prevent accidental mutation of the original DataFrame
        self.data = data.copy()
        
        # Ensure the 'time' column is explicitly treated as UTC datetime
        if not pd.api.types.is_datetime64_any_dtype(self.data['time']):
            self.data['time'] = pd.to_datetime(self.data['time'], format='ISO8601', utc=True)

    @classmethod
    def _validate(cls, df: pd.DataFrame) -> None:
        """
        Internal method to enforce the exact schema requirements.
        """
        missing_cols = [col for col in cls.REQUIRED_COLUMNS if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Invalid schema. Missing required columns: {missing_cols}")

    # ---------------------------------------------------------
    # Import / Export Methods (Round-Trip)
    # ---------------------------------------------------------

    def to_csv(self, filepath: str) -> None:
        """
        Exports the catalog DataFrame to a human-readable CSV file.
        """
        self.data.to_csv(filepath, index=False)

    @classmethod
    def from_csv(cls, filepath: str) -> 'Catalog':
        """
        Imports a CSV file and returns an instantiated Catalog object.
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"The file {filepath} does not exist.")
            
        df = pd.read_csv(filepath)
        # Re-parse the time column using ISO8601 to handle missing fractional seconds
        df['time'] = pd.to_datetime(df['time'], format='ISO8601', utc=True)
        return cls(df)

    def to_parquet(self, filepath: str) -> None:
        """
        Exports the catalog DataFrame to a highly compressed Parquet file.
        """
        self.data.to_parquet(filepath, index=False)

    @classmethod
    def from_parquet(cls, filepath: str) -> 'Catalog':
        """
        Imports a Parquet file and returns an instantiated Catalog object.
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"The file {filepath} does not exist.")
            
        df = pd.read_parquet(filepath)
        # Parquet natively preserves datetime objects, so no manual parsing is needed
        return cls(df)

    # ---------------------------------------------------------
    # Utility Methods
    # ---------------------------------------------------------
    
    def __len__(self) -> int:
        """Returns the number of events in the catalog."""
        return len(self.data)
        
    def __repr__(self) -> str:
        """Provides a clean summary when printing the object."""
        return f"<Catalog object: {len(self.data)} events>"