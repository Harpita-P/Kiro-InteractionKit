import cv2
import mediapipe as mp
from dataclasses import dataclass
from typing import Optional

from ..gestures.hand_gestures import is_hand_closed, is_pinch_gesture, is_peace_sign, is_thumbs_up, is_thumbs_down, is_rock_sign, is_open_hand, is_pointing, is_ok_sign


mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles


@dataclass
class HandTrackingState:
    """Simple representation of the current hand state.

    Attributes
    ----------
    is_present: Whether a hand is currently detected.
    is_closed: Whether the hand is considered closed (fist) based on landmarks.
    is_pinch: Whether the thumb and index fingertips are close enough to be
        considered a pinch gesture.
    cursor_x: Normalized x position (0-1) of the cursor, based on a fingertip.
    cursor_y: Normalized y position (0-1) of the cursor, based on a fingertip.
    handedness: "Left" or "Right" if available from Mediapipe, otherwise None.
    landmarks: Raw landmark data from MediaPipe (list of landmarks with x, y, z coordinates).
    """
    is_present: bool = False
    is_closed: bool = False
    is_pinch: bool = False
    is_peace: bool = False
    is_thumbs_up: bool = False
    is_thumbs_down: bool = False
    is_rock_sign: bool = False
    is_open_hand: bool = False
    is_pointing: bool = False
    is_ok_sign: bool = False
    cursor_x: Optional[float] = None
    cursor_y: Optional[float] = None
    handedness: Optional[str] = None
    landmarks: Optional[list] = None


class HandTracker:
    """Hand tracking and gesture detection using Mediapipe.

    This class is purposely decoupled from any specific game framework.
    You can use `process_frame` in your own loop (e.g., Pygame, OpenCV, etc.)
    to read the current `HandState` and drive your game logic.
    """

    def __init__(
        self,
        min_detection_confidence: float = 0.5,
        min_tracking_confidence: float = 0.5,
        max_num_hands: int = 1,
        close_threshold: float = 0.01,
        pinch_threshold: float = 0.05,
    ) -> None:
        self._hands = mp_hands.Hands(
            max_num_hands=max_num_hands,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence,
        )
        self._close_threshold = close_threshold
        self._pinch_threshold = pinch_threshold
        self.state = HandTrackingState()

    def process_frame(self, frame_bgr):
        """Process a BGR frame (as from OpenCV) and update internal hand state.

        Parameters
        ----------
        frame_bgr: np.ndarray
            BGR image from a camera or video (e.g., `cap.read()` from OpenCV).

        Returns
        -------
        frame_bgr: np.ndarray
            The same frame, optionally annotated with landmarks.
        HandState
            The updated hand state instance for convenience.
        """
        # Convert BGR to RGB and mark non-writeable to speed up processing
        image = cv2.cvtColor(cv2.flip(frame_bgr, 1), cv2.COLOR_BGR2RGB)
        image.flags.writeable = False

        results = self._hands.process(image)

        # Prepare for drawing
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        # Default state when no hand is present
        self.state = HandTrackingState(
            is_present=False,
            is_closed=False,
            is_pinch=False,
            is_peace=False,
            is_thumbs_up=False,
            is_thumbs_down=False,
            is_rock_sign=False,
            is_open_hand=False,
            is_pointing=False,
            is_ok_sign=False,
            cursor_x=None,
            cursor_y=None,
            handedness=None,
            landmarks=None,
        )

        if results.multi_hand_landmarks:
            # For now, just consider the first detected hand
            hand_landmarks = results.multi_hand_landmarks[0]

            # Determine handedness if available
            handedness = None
            if results.multi_handedness:
                handedness = results.multi_handedness[0].classification[0].label

            # Landmark drawing disabled for cleaner display
            # (Only cursor dot will be shown in the application)

            # Landmarks for different gesture logics
            lms = hand_landmarks.landmark

            # Gesture detection is delegated to reusable helpers in
            # kiro_interaction_kit.gestures.hand_gestures so new gestures can be added easily.
            is_closed = is_hand_closed(lms, close_threshold=self._close_threshold)
            is_pinch = is_pinch_gesture(lms, pinch_threshold=self._pinch_threshold)
            is_peace = is_peace_sign(lms)
            is_thumbs_up_detected = is_thumbs_up(lms)
            is_thumbs_down_detected = is_thumbs_down(lms)
            is_rock_sign_detected = is_rock_sign(lms)
            is_open_hand_detected = is_open_hand(lms)
            is_pointing_detected = is_pointing(lms)
            is_ok_sign_detected = is_ok_sign(lms)

            # Cursor position based on index fingertip (normalized 0-1)
            index_tip = lms[8]
            cursor_x = index_tip.x
            cursor_y = index_tip.y

            self.state = HandTrackingState(
                is_present=True,
                is_closed=is_closed,
                is_pinch=is_pinch,
                is_peace=is_peace,
                is_thumbs_up=is_thumbs_up_detected,
                is_thumbs_down=is_thumbs_down_detected,
                is_rock_sign=is_rock_sign_detected,
                is_open_hand=is_open_hand_detected,
                is_pointing=is_pointing_detected,
                is_ok_sign=is_ok_sign_detected,
                cursor_x=cursor_x,
                cursor_y=cursor_y,
                handedness=handedness,
                landmarks=lms,
            )

            # Text overlay removed for cleaner display

            # Draw a red dot cursor at the fingertip position, scaled
            # to the current frame size.
            h, w = image.shape[:2]
            cursor_px = int(cursor_x * w)
            cursor_py = int(cursor_y * h)
            cv2.circle(image, (cursor_px, cursor_py), 10, (0, 0, 255), -1)

        return image, self.state

    def close(self):
        """Release Mediapipe resources."""
        if self._hands is not None:
            self._hands.close()


# Backwards-compatible aliases for existing code
HandState = HandTrackingState
HandController = HandTracker
