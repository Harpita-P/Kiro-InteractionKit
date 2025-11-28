def is_thumbs_down(landmarks, curl_threshold: float = 0.05) -> bool:
    """Return True if the hand forms a thumbs down gesture.
    
    Heuristic:
    - Thumb (4) is extended downward (tip lower than IP joint)
    - All other fingers are curled (fingertips below their PIP joints)
    """
    thumb_tip = landmarks[4]
    thumb_ip = landmarks[3]
    
    # Other fingers: check if curled
    fingers = {
        'index': (8, 6),
        'middle': (12, 10),
        'ring': (16, 14),
        'pinky': (20, 18)
    }
    
    # Thumb should be extended downward
    thumb_extended = thumb_tip.y - curl_threshold > thumb_ip.y
    
    # All other fingers should be curled
    all_curled = all(
        landmarks[tip].y >= landmarks[pip].y - curl_threshold
        for tip, pip in fingers.values()
    )
    
    return thumb_extended and all_curled