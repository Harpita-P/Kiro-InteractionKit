def is_nod_up(x_axis: float, threshold: float = 15.0) -> bool:
    """Return True if head is nodding up (looking up).
    
    Args:
        x_axis: Head rotation around x-axis in degrees (positive = up, negative = down)
        threshold: Minimum angle in degrees to consider as nodding up
    
    Returns:
        True if head is tilted up beyond threshold
    """
    return x_axis > threshold
