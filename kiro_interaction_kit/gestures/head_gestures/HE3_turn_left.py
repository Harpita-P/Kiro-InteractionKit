def is_turn_left(y_axis: float, threshold: float = 20.0) -> bool:
    """Return True if head is turning left.
    
    Args:
        y_axis: Head rotation around y-axis in degrees (positive = right, negative = left)
        threshold: Minimum angle in degrees to consider as turning left
    
    Returns:
        True if head is turned left beyond threshold
    """
    return y_axis < -threshold
