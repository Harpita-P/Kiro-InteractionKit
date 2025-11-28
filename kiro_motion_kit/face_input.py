from dataclasses import dataclass
from typing import Optional

from .face_controller import FaceTracker, FaceTrackingState


@dataclass
class FaceInputSnapshot:
    """High-level, game-friendly face input actions for a single frame.

    These are derived from low-level FaceTrackingState but avoid any CV details.
    """

    # Continuous state
    is_present: bool = False
    is_blink: bool = False
    is_mouth_open: bool = False
    is_smiling: bool = False

    # Edge events (one-frame pulses)
    blink_pressed: bool = False   # eyes open -> blink
    blink_released: bool = False  # blink -> eyes open
    mouth_open_pressed: bool = False    # mouth closed -> mouth open
    mouth_open_released: bool = False   # mouth open -> mouth closed
    smiling_pressed: bool = False    # not smiling -> smiling
    smiling_released: bool = False   # smiling -> not smiling


class FaceInputManager:
    """Adapter that turns FaceTracker output into game-friendly actions.

    Usage (per frame in your game loop):

        actions, frame = face_input.update_from_camera(cap)

    Or if you already have a frame:

        actions, annotated = face_input.update_from_frame(frame)

    """

    def __init__(self, controller: Optional[FaceTracker] = None) -> None:
        self.controller = controller or FaceTracker()
        self._prev_state: Optional[FaceTrackingState] = None

    @property
    def raw_controller(self) -> FaceTracker:
        """Access the underlying FaceTracker if needed."""
        return self.controller

    def _compute_actions(self, state: FaceTrackingState) -> FaceInputSnapshot:
        """Convert FaceTrackingState + previous state into FaceInputSnapshot with edges."""
        prev = self._prev_state

        blink_pressed = False
        blink_released = False
        mouth_open_pressed = False
        mouth_open_released = False
        smiling_pressed = False
        smiling_released = False

        if prev is not None:
            if not prev.is_blink and state.is_blink:
                blink_pressed = True
            if prev.is_blink and not state.is_blink:
                blink_released = True

            if not prev.is_mouth_open and state.is_mouth_open:
                mouth_open_pressed = True
            if prev.is_mouth_open and not state.is_mouth_open:
                mouth_open_released = True

            if not prev.is_smiling and state.is_smiling:
                smiling_pressed = True
            if prev.is_smiling and not state.is_smiling:
                smiling_released = True

        actions = FaceInputSnapshot(
            is_present=state.is_present,
            is_blink=state.is_blink,
            is_mouth_open=state.is_mouth_open,
            is_smiling=state.is_smiling,
            blink_pressed=blink_pressed,
            blink_released=blink_released,
            mouth_open_pressed=mouth_open_pressed,
            mouth_open_released=mouth_open_released,
            smiling_pressed=smiling_pressed,
            smiling_released=smiling_released,
        )

        self._prev_state = state
        return actions

    def update_from_frame(self, frame_bgr):
        """Process an existing BGR frame and return (actions, annotated_frame)."""
        annotated, state = self.controller.process_frame(frame_bgr)
        actions = self._compute_actions(state)
        return actions, annotated

    def update_from_camera(self, cap):
        """Read from an OpenCV VideoCapture and return (actions, annotated_frame).

        This is a convenience helper. It expects `cap.read()` semantics.
        """
        success, frame = cap.read()
        if not success:
            return FaceInputSnapshot(), None

        return self.update_from_frame(frame)

    def close(self):
        self.controller.close()


# Backwards-compatible aliases
FaceInput = FaceInputManager
FaceActions = FaceInputSnapshot
