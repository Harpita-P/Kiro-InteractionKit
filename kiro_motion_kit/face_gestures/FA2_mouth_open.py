import math


def is_mouth_open(landmarks, threshold: float = 0.03) -> bool:
    """Return True if mouth is open.
    
    Uses Mouth Aspect Ratio (MAR) to detect mouth opening.
    MediaPipe Face Mesh landmark indices:
    - Upper lip: 13
    - Lower lip: 14
    - Left mouth corner: 78
    - Right mouth corner: 308
    
    Args:
        landmarks: Face mesh landmarks from MediaPipe
        threshold: MAR threshold above which mouth is considered open
    
    Returns:
        True if mouth is open
    """
    # Vertical distance (upper lip to lower lip)
    vertical = math.sqrt(
        (landmarks[13].x - landmarks[14].x) ** 2 +
        (landmarks[13].y - landmarks[14].y) ** 2 +
        (landmarks[13].z - landmarks[14].z) ** 2
    )
    
    # Horizontal distance (left corner to right corner)
    horizontal = math.sqrt(
        (landmarks[78].x - landmarks[308].x) ** 2 +
        (landmarks[78].y - landmarks[308].y) ** 2 +
        (landmarks[78].z - landmarks[308].z) ** 2
    )
    
    # Mouth Aspect Ratio
    mar = vertical / horizontal if horizontal > 0 else 0
    
    return mar > threshold
