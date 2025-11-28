def is_nod_down(x_axis: float, threshold: float = -15.0) -> bool:
    """Return True if head is nodding down (looking down).
    
    Args:
        x_axis: Head rotation around x-axis in degrees (positive = up, negative = down)
        threshold: Maximum angle in degrees to consider as nodding down
    
    Returns:
        True if head is tilted down beyond threshold
    """
    return x_axis < threshold
