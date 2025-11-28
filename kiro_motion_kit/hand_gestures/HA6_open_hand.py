def is_open_hand(landmarks, extension_threshold: float = 0.1) -> bool:
    """Return True if the hand is fully open with fingers spread.
    
    Heuristic:
    - All fingertips are extended (above their PIP joints)
    - All fingers are reasonably spread apart
    """
    fingers = {
        'thumb': (4, 3),
        'index': (8, 6),
        'middle': (12, 10),
        'ring': (16, 14),
        'pinky': (20, 18)
    }
    
    # All tips should be extended
    all_extended = all(
        landmarks[tip].y + extension_threshold < landmarks[pip].y
        for tip, pip in fingers.values()
    )
    
    if not all_extended:
        return False
    
    # Check that fingers are spread (tips should have some horizontal separation)
    tips = [landmarks[8].x, landmarks[12].x, landmarks[16].x, landmarks[20].x]
    spread = max(tips) - min(tips)
    
    return spread > 0.15