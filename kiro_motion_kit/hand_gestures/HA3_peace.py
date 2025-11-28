def is_peace_sign(landmarks, tip_gap_threshold: float = 0.05, curl_threshold: float = 0.05) -> bool:
    """Return True if the hand roughly forms a peace / victory sign.

    Very simple heuristic based on Mediapipe landmarks:
    - Index (8) and middle (12) fingertips are extended (higher than their
      respective PIP joints 6 and 10).
    - Ring (16) and pinky (20) fingertips are curled (not much above their PIP
      joints 14 and 18).
    - Index and middle fingertips are reasonably separated horizontally to
      resemble a "V" shape.

    This is intentionally approximate and meant as a starting point that
    developers can refine or replace.
    """

    # Index finger: tip (8) vs PIP (6)
    index_tip = landmarks[8]
    index_pip = landmarks[6]

    # Middle finger: tip (12) vs PIP (10)
    middle_tip = landmarks[12]
    middle_pip = landmarks[10]

    # Ring finger: tip (16) vs PIP (14)
    ring_tip = landmarks[16]
    ring_pip = landmarks[14]

    # Pinky: tip (20) vs PIP (18)
    pinky_tip = landmarks[20]
    pinky_pip = landmarks[18]

    # Mediapipe y: 0 is top, 1 is bottom. Extended means tip.y < pip.y
    index_extended = index_tip.y + curl_threshold < index_pip.y
    middle_extended = middle_tip.y + curl_threshold < middle_pip.y

    ring_curled = ring_tip.y >= ring_pip.y - curl_threshold
    pinky_curled = pinky_tip.y >= pinky_pip.y - curl_threshold

    if not (index_extended and middle_extended and ring_curled and pinky_curled):
        return False

    # Ensure index and middle tips are separated horizontally (forming a V)
    if abs(index_tip.x - middle_tip.x) < tip_gap_threshold:
        return False

    return True
