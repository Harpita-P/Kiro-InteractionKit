def is_turn_right(y_axis: float, threshold: float = 20.0) -> bool:
    """Return True if head is turning right.
    
    Args:
        y_axis: Head rotation around y-axis in degrees (positive = right, negative = left)
        threshold: Minimum angle in degrees to consider as turning right
    
    Returns:
        True if head is turned right beyond threshold
    """
    return y_axis > threshold
