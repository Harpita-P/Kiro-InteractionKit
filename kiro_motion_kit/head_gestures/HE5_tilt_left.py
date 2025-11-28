def is_tilt_left(z_axis: float, threshold: float = 15.0) -> bool:
    """Return True if head is tilting left.
    
    Args:
        z_axis: Head rotation around z-axis in degrees (positive = right tilt, negative = left tilt)
        threshold: Minimum angle in degrees to consider as tilting left
    
    Returns:
        True if head is tilted left beyond threshold
    """
    return z_axis < -threshold
