import cv2
import mediapipe as mp
from dataclasses import dataclass
from typing import Optional

from .face_gestures import is_blink, is_mouth_open, is_smiling


mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles


@dataclass
class FaceTrackingState:
    """Simple representation of the current face state.

    Attributes
    ----------
    is_present: Whether a face is currently detected.
    is_blink: Whether both eyes are closed (blink detected).
    is_mouth_open: Whether the mouth is open.
    is_smiling: Whether the person is smiling.
    landmarks: Raw face landmarks from MediaPipe (468 points).
    """
    is_present: bool = False
    is_blink: bool = False
    is_mouth_open: bool = False
    is_smiling: bool = False
    landmarks: Optional[list] = None


class FaceTracker:
    """Face tracking and gesture detection using MediaPipe Face Mesh.

    This class detects facial expressions like blinks, mouth open/closed,
    and smiling using MediaPipe's 468-point face mesh.
    """

    def __init__(
        self,
        min_detection_confidence: float = 0.5,
        min_tracking_confidence: float = 0.5,
        max_num_faces: int = 1,
    ) -> None:
        self._face_mesh = mp_face_mesh.FaceMesh(
            max_num_faces=max_num_faces,
            refine_landmarks=True,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence,
        )
        self.state = FaceTrackingState()

    def process_frame(self, frame_bgr):
        """Process a BGR frame and update internal face state.

        Parameters
        ----------
        frame_bgr: np.ndarray
            BGR image from a camera or video.

        Returns
        -------
        frame_bgr: np.ndarray
            The same frame, optionally annotated with landmarks.
        FaceTrackingState
            The updated face state instance.
        """
        # Convert BGR to RGB
        image = cv2.cvtColor(cv2.flip(frame_bgr, 1), cv2.COLOR_BGR2RGB)
        image.flags.writeable = False

        results = self._face_mesh.process(image)

        # Prepare for drawing
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        # Default state when no face is present
        self.state = FaceTrackingState(
            is_present=False,
            is_blink=False,
            is_mouth_open=False,
            is_smiling=False,
            landmarks=None,
        )

        if results.multi_face_landmarks:
            face_landmarks = results.multi_face_landmarks[0]

            # Draw face mesh
            mp_drawing.draw_landmarks(
                image=image,
                landmark_list=face_landmarks,
                connections=mp_face_mesh.FACEMESH_TESSELATION,
                landmark_drawing_spec=None,
                connection_drawing_spec=mp_drawing_styles
                .get_default_face_mesh_tesselation_style()
            )
            mp_drawing.draw_landmarks(
                image=image,
                landmark_list=face_landmarks,
                connections=mp_face_mesh.FACEMESH_CONTOURS,
                landmark_drawing_spec=None,
                connection_drawing_spec=mp_drawing_styles
                .get_default_face_mesh_contours_style()
            )

            lms = face_landmarks.landmark

            # Gesture detection
            is_blink_detected = is_blink(lms)
            is_mouth_open_detected = is_mouth_open(lms)
            is_smiling_detected = is_smiling(lms)

            self.state = FaceTrackingState(
                is_present=True,
                is_blink=is_blink_detected,
                is_mouth_open=is_mouth_open_detected,
                is_smiling=is_smiling_detected,
                landmarks=lms,
            )

            # Overlay state text
            blink_text = "BLINK" if is_blink_detected else "EYES OPEN"
            mouth_text = "MOUTH OPEN" if is_mouth_open_detected else "MOUTH CLOSED"
            smile_text = "SMILING" if is_smiling_detected else "NOT SMILING"

            cv2.putText(image, blink_text, (10, 110), cv2.FONT_HERSHEY_SIMPLEX,
                        1.0, (0, 255, 0) if not is_blink_detected else (0, 0, 255), 2, cv2.LINE_AA)
            cv2.putText(image, mouth_text, (10, 150), cv2.FONT_HERSHEY_SIMPLEX,
                        1.0, (0, 255, 0) if not is_mouth_open_detected else (0, 0, 255), 2, cv2.LINE_AA)
            cv2.putText(image, smile_text, (10, 190), cv2.FONT_HERSHEY_SIMPLEX,
                        1.0, (0, 255, 0) if is_smiling_detected else (255, 0, 0), 2, cv2.LINE_AA)

        return image, self.state

    def close(self):
        """Release MediaPipe resources."""
        if self._face_mesh is not None:
            self._face_mesh.close()
