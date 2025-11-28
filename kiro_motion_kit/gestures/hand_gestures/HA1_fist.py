def is_hand_closed(landmarks, close_threshold: float = 0.01) -> bool:
    """Return True if the hand is considered closed (fist).

    Uses Mediapipe hand landmarks:
    - 9: base of the middle finger (near the palm)
    - 12: tip of the middle finger

    Mediapipe uses normalized coordinates where y=0 is top and y=1 is bottom.
    When landmark 12 is lower than 9 (12.y > 9.y) by more than a small threshold,
    we treat the hand as closed.
    """

    y9 = landmarks[9].y
    y12 = landmarks[12].y

    return (y12 - y9) > close_threshold
