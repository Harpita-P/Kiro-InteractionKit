def is_tilt_right(z_axis: float, threshold: float = 15.0) -> bool:
    """Return True if head is tilting right.
    
    Args:
        z_axis: Head rotation around z-axis in degrees (positive = right tilt, negative = left tilt)
        threshold: Minimum angle in degrees to consider as tilting right
    
    Returns:
        True if head is tilted right beyond threshold
    """
    return z_axis > threshold
