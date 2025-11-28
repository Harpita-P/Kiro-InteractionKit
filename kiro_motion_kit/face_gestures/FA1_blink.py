import math


def is_blink(landmarks, threshold: float = 0.02) -> bool:
    """Return True if both eyes are closed (blink detected).
    
    Uses Eye Aspect Ratio (EAR) to detect eye closure.
    MediaPipe Face Mesh landmark indices:
    - Left eye: 159 (top), 145 (bottom), 33 (left), 133 (right)
    - Right eye: 386 (top), 374 (bottom), 263 (left), 362 (right)
    
    Args:
        landmarks: Face mesh landmarks from MediaPipe
        threshold: EAR threshold below which eye is considered closed
    
    Returns:
        True if both eyes are closed
    """
    def eye_aspect_ratio(top, bottom, left, right):
        """Calculate Eye Aspect Ratio (EAR)."""
        # Vertical distance
        vertical = math.sqrt(
            (top.x - bottom.x) ** 2 +
            (top.y - bottom.y) ** 2 +
            (top.z - bottom.z) ** 2
        )
        # Horizontal distance
        horizontal = math.sqrt(
            (left.x - right.x) ** 2 +
            (left.y - right.y) ** 2 +
            (left.z - right.z) ** 2
        )
        return vertical / horizontal if horizontal > 0 else 0
    
    # Left eye EAR
    left_ear = eye_aspect_ratio(
        landmarks[159],  # top
        landmarks[145],  # bottom
        landmarks[33],   # left
        landmarks[133]   # right
    )
    
    # Right eye EAR
    right_ear = eye_aspect_ratio(
        landmarks[386],  # top
        landmarks[374],  # bottom
        landmarks[263],  # left
        landmarks[362]   # right
    )
    
    # Both eyes closed
    return left_ear < threshold and right_ear < threshold
