import math


def is_smiling(landmarks, threshold: float = 0.01) -> bool:
    """Return True if person is smiling.
    
    Detects smile by measuring the distance between mouth corners
    relative to the mouth height (Mouth Aspect Ratio for smile).
    MediaPipe Face Mesh landmark indices:
    - Left mouth corner: 61
    - Right mouth corner: 291
    - Upper lip top: 13
    - Lower lip bottom: 14
    
    Args:
        landmarks: Face mesh landmarks from MediaPipe
        threshold: Smile threshold for corner elevation (default 0.01, lower = more sensitive)
    
    Returns:
        True if smiling
    """
    # Mouth corners
    left_corner = landmarks[61]
    right_corner = landmarks[291]
    
    # Mouth vertical points
    upper_lip = landmarks[13]
    lower_lip = landmarks[14]
    
    # Calculate horizontal distance between corners
    mouth_width = math.sqrt(
        (right_corner.x - left_corner.x) ** 2 +
        (right_corner.y - left_corner.y) ** 2
    )
    
    # Calculate vertical distance (mouth height)
    mouth_height = math.sqrt(
        (upper_lip.x - lower_lip.x) ** 2 +
        (upper_lip.y - lower_lip.y) ** 2
    )
    
    # Calculate mouth aspect ratio
    mouth_ratio = mouth_height / mouth_width if mouth_width > 0 else 0
    
    # Also check if corners are raised (y decreases upward in image coordinates)
    mouth_center_y = (upper_lip.y + lower_lip.y) / 2
    corners_avg_y = (left_corner.y + right_corner.y) / 2
    corners_raised = mouth_center_y - corners_avg_y
    
    # Smile detected when mouth is wide (low ratio) and corners are raised
    return mouth_ratio < 0.5 and corners_raised > threshold
