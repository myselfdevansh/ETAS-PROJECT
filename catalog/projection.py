import numpy as np
from pyproj import Proj, Geod

class CoordinateTransformer:
    """
    Handles bidirectional coordinate transformations between spherical (lon, lat)
    and planar Cartesian coordinates (X, Y) in kilometers.
    """
    def __init__(self, center_lon: float, center_lat: float):
        """
        Initializes a local Azimuthal Equidistant (aeqd) projection centered 
        on the given coordinates to minimize regional distance distortion.
        """
        self.center_lon = center_lon
        self.center_lat = center_lat
        
        # Define the projection, explicitly setting units to kilometers
        self.proj = Proj(
            proj="aeqd",
            lat_0=center_lat,
            lon_0=center_lon,
            datum="WGS84",
            units="km"
        )

    def forward(self, lons, lats):
        """
        Converts arrays of longitude and latitude to planar X, Y in kilometers.
        """
        # inverse=False dictates a forward transformation
        x_km, y_km = self.proj(lons, lats, inverse=False)
        return np.array(x_km), np.array(y_km)

    def inverse(self, x_km, y_km):
        """
        Converts arrays of planar X, Y in kilometers back to longitude and latitude.
        """
        # inverse=True dictates a reverse transformation
        lons, lats = self.proj(x_km, y_km, inverse=True)
        return np.array(lons), np.array(lats)


def test_reversibility():
    """
    Tests the transformation to ensure the round-trip error is strictly < 1 meter.
    """
    # 1. Define a center point (e.g., Southern California)
    center_lon, center_lat = -118.0, 34.0
    transformer = CoordinateTransformer(center_lon, center_lat)
    
    # 2. Define an array of test coordinates scattered around the center
    orig_lons = np.array([-118.1, -119.5, -117.0, -118.0])
    orig_lats = np.array([34.1, 35.2, 33.5, 34.0])
    
    # 3. Execute the forward transform (degrees -> km)
    x_km, y_km = transformer.forward(orig_lons, orig_lats)
    
    # 4. Execute the inverse transform (km -> degrees)
    inv_lons, inv_lats = transformer.inverse(x_km, y_km)
    
    # 5. Calculate exact error in meters using the standard WGS84 ellipsoid
    geod = Geod(ellps="WGS84")
    
    # geod.inv returns (forward_azimuth, back_azimuth, distance_in_meters)
    _, _, distances_m = geod.inv(orig_lons, orig_lats, inv_lons, inv_lats)
    
    # 6. Evaluate the maximum spatial error against the constraint
    max_error_m = np.max(distances_m)
    
    assert max_error_m < 1.0, f"Reversibility failed! Max error: {max_error_m} meters"
    
    print(f"Success: Reversibility test passed.")
    print(f"Maximum round-trip error: {max_error_m:.6e} meters")


if __name__ == "__main__":
    # Execute the test when the file is run directly
    test_reversibility()