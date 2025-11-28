def is_pointing(landmarks, curl_threshold: float = 0.05) -> bool:
    """Return True if the hand is pointing with index finger.
    
    Heuristic:
    - Index (8) is extended
    - Other fingers are curled
    """
    index_tip = landmarks[8]
    index_pip = landmarks[6]
    
    fingers_to_curl = {
        'middle': (12, 10),
        'ring': (16, 14),
        'pinky': (20, 18)
    }
    
    index_extended = index_tip.y + curl_threshold < index_pip.y
    others_curled = all(
        landmarks[tip].y >= landmarks[pip].y - curl_threshold
        for tip, pip in fingers_to_curl.values()
    )
    
    return index_extended and others_curled