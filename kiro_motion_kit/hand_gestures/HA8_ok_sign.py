def is_ok_sign(landmarks, curl_threshold: float = 0.05, distance_threshold: float = 0.05) -> bool:
    """Return True if the hand forms an 'OK' sign.
    
    Heuristic:
    - Thumb (4) and index (8) fingertips are very close (forming a circle)
    - Middle (12), ring (16), and pinky (20) are extended upward
    """
    thumb_tip = landmarks[4]
    index_tip = landmarks[8]
    index_pip = landmarks[6]
    
    middle_tip = landmarks[12]
    middle_pip = landmarks[10]
    ring_tip = landmarks[16]
    ring_pip = landmarks[14]
    pinky_tip = landmarks[20]
    pinky_pip = landmarks[18]
    
    # Thumb and index tips should be close together
    distance = ((thumb_tip.x - index_tip.x) ** 2 + (thumb_tip.y - index_tip.y) ** 2) ** 0.5
    thumb_index_touching = distance < distance_threshold
    
    # Middle, ring, pinky should be extended
    middle_extended = middle_tip.y + curl_threshold < middle_pip.y
    ring_extended = ring_tip.y + curl_threshold < ring_pip.y
    pinky_extended = pinky_tip.y + curl_threshold < pinky_pip.y
    
    return thumb_index_touching and middle_extended and ring_extended and pinky_extended
