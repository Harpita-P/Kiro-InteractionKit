def is_pinch_gesture(landmarks, pinch_threshold: float = 0.05) -> bool:
    """Return True if thumb tip and index tip are close enough to be a pinch.

    Uses Mediapipe hand landmarks:
    - 4: thumb tip
    - 8: index finger tip

    Computes Euclidean distance in normalized (x,y) space and compares to a
    configurable threshold to decide if the gesture is a pinch.
    """

    thumb_tip = landmarks[4]
    index_tip = landmarks[8]

    dx = thumb_tip.x - index_tip.x
    dy = thumb_tip.y - index_tip.y
    distance = (dx * dx + dy * dy) ** 0.5

    return distance < pinch_threshold
