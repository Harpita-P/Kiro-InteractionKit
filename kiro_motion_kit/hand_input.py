from dataclasses import dataclass
from typing import Optional

from .hand_controller import HandTracker, HandTrackingState


@dataclass
class HandInputSnapshot:
    """High-level, game-friendly hand input actions for a single frame.

    These are derived from low-level HandState but avoid any CV details.
    """

    # Continuous state
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

    # Edge events (one-frame pulses)
    closed_pressed: bool = False   # open -> closed
    closed_released: bool = False  # closed -> open
    pinch_pressed: bool = False    # not pinch -> pinch
    pinch_released: bool = False   # pinch -> not pinch
    peace_pressed: bool = False    # not peace -> peace
    peace_released: bool = False   # peace -> not peace
    thumbs_up_pressed: bool = False    # not thumbs_up -> thumbs_up
    thumbs_up_released: bool = False   # thumbs_up -> not thumbs_up
    thumbs_down_pressed: bool = False    # not thumbs_down -> thumbs_down
    thumbs_down_released: bool = False   # thumbs_down -> not thumbs_down
    rock_sign_pressed: bool = False    # not rock_sign -> rock_sign
    rock_sign_released: bool = False   # rock_sign -> not rock_sign
    open_hand_pressed: bool = False    # not open_hand -> open_hand
    open_hand_released: bool = False   # open_hand -> not open_hand
    pointing_pressed: bool = False    # not pointing -> pointing
    pointing_released: bool = False   # pointing -> not pointing
    ok_sign_pressed: bool = False    # not ok_sign -> ok_sign
    ok_sign_released: bool = False   # ok_sign -> not ok_sign


class HandInputManager:
    """Adapter that turns HandController output into game-friendly actions.

    Usage (per frame in your game loop):

        actions, frame = hand_input.update_from_camera(cap)

    Or if you already have a frame:

        actions, annotated = hand_input.update_from_frame(frame)

    """

    def __init__(self, controller: Optional[HandTracker] = None) -> None:
        self.controller = controller or HandTracker()
        self._prev_state: Optional[HandTrackingState] = None

    @property
    def raw_controller(self) -> HandTracker:
        """Access the underlying HandController if needed."""
        return self.controller

    def _compute_actions(self, state: HandTrackingState) -> HandInputSnapshot:
        """Convert HandState + previous state into HandActions with edges."""
        prev = self._prev_state

        closed_pressed = False
        closed_released = False
        pinch_pressed = False
        pinch_released = False
        peace_pressed = False
        peace_released = False
        thumbs_up_pressed = False
        thumbs_up_released = False
        thumbs_down_pressed = False
        thumbs_down_released = False
        rock_sign_pressed = False
        rock_sign_released = False
        open_hand_pressed = False
        open_hand_released = False
        pointing_pressed = False
        pointing_released = False
        ok_sign_pressed = False
        ok_sign_released = False

        if prev is not None:
            if not prev.is_closed and state.is_closed:
                closed_pressed = True
            if prev.is_closed and not state.is_closed:
                closed_released = True

            if not prev.is_pinch and state.is_pinch:
                pinch_pressed = True
            if prev.is_pinch and not state.is_pinch:
                pinch_released = True

            if not prev.is_peace and state.is_peace:
                peace_pressed = True
            if prev.is_peace and not state.is_peace:
                peace_released = True

            if not prev.is_thumbs_up and state.is_thumbs_up:
                thumbs_up_pressed = True
            if prev.is_thumbs_up and not state.is_thumbs_up:
                thumbs_up_released = True

            if not prev.is_thumbs_down and state.is_thumbs_down:
                thumbs_down_pressed = True
            if prev.is_thumbs_down and not state.is_thumbs_down:
                thumbs_down_released = True

            if not prev.is_rock_sign and state.is_rock_sign:
                rock_sign_pressed = True
            if prev.is_rock_sign and not state.is_rock_sign:
                rock_sign_released = True

            if not prev.is_open_hand and state.is_open_hand:
                open_hand_pressed = True
            if prev.is_open_hand and not state.is_open_hand:
                open_hand_released = True

            if not prev.is_pointing and state.is_pointing:
                pointing_pressed = True
            if prev.is_pointing and not state.is_pointing:
                pointing_released = True

            if not prev.is_ok_sign and state.is_ok_sign:
                ok_sign_pressed = True
            if prev.is_ok_sign and not state.is_ok_sign:
                ok_sign_released = True

        actions = HandInputSnapshot(
            is_present=state.is_present,
            is_closed=state.is_closed,
            is_pinch=state.is_pinch,
            is_peace=state.is_peace,
            is_thumbs_up=state.is_thumbs_up,
            is_thumbs_down=state.is_thumbs_down,
            is_rock_sign=state.is_rock_sign,
            is_open_hand=state.is_open_hand,
            is_pointing=state.is_pointing,
            is_ok_sign=state.is_ok_sign,
            cursor_x=state.cursor_x,
            cursor_y=state.cursor_y,
            handedness=state.handedness,
            closed_pressed=closed_pressed,
            closed_released=closed_released,
            pinch_pressed=pinch_pressed,
            pinch_released=pinch_released,
            peace_pressed=peace_pressed,
            peace_released=peace_released,
            thumbs_up_pressed=thumbs_up_pressed,
            thumbs_up_released=thumbs_up_released,
            thumbs_down_pressed=thumbs_down_pressed,
            thumbs_down_released=thumbs_down_released,
            rock_sign_pressed=rock_sign_pressed,
            rock_sign_released=rock_sign_released,
            open_hand_pressed=open_hand_pressed,
            open_hand_released=open_hand_released,
            pointing_pressed=pointing_pressed,
            pointing_released=pointing_released,
            ok_sign_pressed=ok_sign_pressed,
            ok_sign_released=ok_sign_released,
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
            return HandInputSnapshot(), None

        return self.update_from_frame(frame)

    def close(self):
        self.controller.close()


# Backwards-compatible aliases
HandInput = HandInputManager
HandActions = HandInputSnapshot
