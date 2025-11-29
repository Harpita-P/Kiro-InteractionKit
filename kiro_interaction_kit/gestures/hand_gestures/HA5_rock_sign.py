def is_rock_sign(landmarks, tip_gap_threshold: float = 0.05, curl_threshold: float = 0.05) -> bool:
    """Return True if the hand forms a rock/devil horns sign.
    
    Heuristic:
    - Index (8) and pinky (20) are extended upward
    - Middle (12) and ring (16) are curled
    - Index and pinky are separated horizontally
    """
    index_tip = landmarks[8]
    index_pip = landmarks[6]
    middle_tip = landmarks[12]
    middle_pip = landmarks[10]
    ring_tip = landmarks[16]
    ring_pip = landmarks[14]
    pinky_tip = landmarks[20]
    pinky_pip = landmarks[18]
    
    index_extended = index_tip.y + curl_threshold < index_pip.y
    pinky_extended = pinky_tip.y + curl_threshold < pinky_pip.y
    
    middle_curled = middle_tip.y >= middle_pip.y - curl_threshold
    ring_curled = ring_tip.y >= ring_pip.y - curl_threshold
    
    # Index and pinky should be separated
    separated = abs(index_tip.x - pinky_tip.x) > tip_gap_threshold
    
    return index_extended and pinky_extended and middle_curled and ring_curled and separated
