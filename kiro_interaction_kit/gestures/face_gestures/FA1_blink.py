import math


def is_blink(landmarks, threshold: float = 0.21) -> bool:
    """Return True if both eyes are closed (blink detected).
    
    Uses Eye Aspect Ratio (EAR) to detect eye closure.
    MediaPipe Face Mesh landmark indices (using 6 points per eye):
    - Left eye: 362, 385, 387, 263, 373, 380
    - Right eye: 33, 160, 158, 133, 153, 144
    
    Args:
        landmarks: Face mesh landmarks from MediaPipe
        threshold: EAR threshold below which eye is considered closed (default 0.21)
    
    Returns:
        True if both eyes are closed
    """
    def eye_aspect_ratio(p1, p2, p3, p4, p5, p6):
        """Calculate Eye Aspect Ratio (EAR) using 6 points.
        
        EAR = (||p2-p6|| + ||p3-p5||) / (2 * ||p1-p4||)
        """
        # Vertical distances
        v1 = math.sqrt((p2.x - p6.x) ** 2 + (p2.y - p6.y) ** 2)
        v2 = math.sqrt((p3.x - p5.x) ** 2 + (p3.y - p5.y) ** 2)
        
        # Horizontal distance
        h = math.sqrt((p1.x - p4.x) ** 2 + (p1.y - p4.y) ** 2)
        
        return (v1 + v2) / (2.0 * h) if h > 0 else 0
    
    # Left eye EAR (landmarks: 362, 385, 387, 263, 373, 380)
    left_ear = eye_aspect_ratio(
        landmarks[362], landmarks[385], landmarks[387],
        landmarks[263], landmarks[373], landmarks[380]
    )
    
    # Right eye EAR (landmarks: 33, 160, 158, 133, 153, 144)
    right_ear = eye_aspect_ratio(
        landmarks[33], landmarks[160], landmarks[158],
        landmarks[133], landmarks[153], landmarks[144]
    )
    
    # Average EAR
    avg_ear = (left_ear + right_ear) / 2.0
    
    # Both eyes closed when EAR is below threshold
    return avg_ear < threshold
