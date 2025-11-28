import math


def is_smiling(landmarks, threshold: float = 0.015) -> bool:
    """Return True if person is smiling.
    
    Detects smile by measuring the upward movement of mouth corners
    relative to the mouth center.
    MediaPipe Face Mesh landmark indices:
    - Left mouth corner: 61
    - Right mouth corner: 291
    - Upper lip center: 0
    - Lower lip center: 17
    
    Args:
        landmarks: Face mesh landmarks from MediaPipe
        threshold: Smile threshold for corner elevation
    
    Returns:
        True if smiling
    """
    # Mouth center y-coordinate (average of upper and lower lip center)
    mouth_center_y = (landmarks[0].y + landmarks[17].y) / 2
    
    # Left and right mouth corner y-coordinates
    left_corner_y = landmarks[61].y
    right_corner_y = landmarks[291].y
    
    # Calculate how much corners are raised above center
    left_elevation = mouth_center_y - left_corner_y
    right_elevation = mouth_center_y - right_corner_y
    
    # Both corners should be elevated for a smile
    return left_elevation > threshold and right_elevation > threshold
