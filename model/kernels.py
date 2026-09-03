import numpy as np

def omori_utsu(t: np.ndarray, c: float, p: float) -> np.ndarray:
    """
    Temporal decay kernel (Omori-Utsu).
    Returns the triggering rate at time t after an earthquake.
    """
    # Force negative times to 0 just in case, though they shouldn't occur
    t = np.maximum(t, 0)
    return (t + c) ** (-p)

def omori_integral(t: float, c: float, p: float) -> float:
    """
    Integral of the Omori-Utsu kernel from 0 to t.
    Used for computing the total expected number of aftershocks in a time window.
    """
    t = max(t, 0.0)
    if p == 1.0:
        return np.log(t + c) - np.log(c)
    return ((t + c)**(1 - p) - c**(1 - p)) / (1 - p)

def spatial_power_law(r: np.ndarray, d: float, q: float) -> np.ndarray:
    """
    Spatial kernel (normalized power-law).
    r is the distance in km from the epicenter.
    """
    return (q - 1) / (np.pi * d**2) * (1 + (r**2) / (d**2)) ** (-q)

def productivity(m: np.ndarray, mc: float, k: float, alpha: float) -> np.ndarray:
    """
    Number of expected aftershocks for an event of magnitude m.
    """
    return k * np.exp(alpha * (m - mc))
