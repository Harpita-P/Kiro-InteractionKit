from typing import Any, Dict, Union

from ..hand_input import HandInputSnapshot
from ..face_input import FaceInputSnapshot
from .event_bus import get_event_bus


def dispatch_gesture_events(snapshot: Union[HandInputSnapshot, FaceInputSnapshot]) -> None:
    """Translate a HandInputSnapshot or FaceInputSnapshot into high-level gesture.* events.

    This function does *no* game logic. It only looks at gesture edges and
    continuous state, and emits events through the EventBus.

    Example events:
    - gesture.closed.start
    - gesture.closed.end
    - gesture.pinch.start
    - gesture.pinch.end
    - gesture.blink.start
    - gesture.blink.end
    - gesture.mouth_open.start
    - gesture.mouth_open.end

    Each event payload contains relevant state information.
    """

    bus = get_event_bus()

    # Handle FaceInputSnapshot
    if isinstance(snapshot, FaceInputSnapshot):
        base: Dict[str, Any] = {
            "is_blink": snapshot.is_blink,
            "is_mouth_open": snapshot.is_mouth_open,
            "is_smiling": snapshot.is_smiling,
        }

        if snapshot.blink_pressed:
            bus.fire("gesture.blink.start", base)

        if snapshot.blink_released:
            bus.fire("gesture.blink.end", base)

        if snapshot.mouth_open_pressed:
            bus.fire("gesture.mouth_open.start", base)

        if snapshot.mouth_open_released:
            bus.fire("gesture.mouth_open.end", base)

        if snapshot.smiling_pressed:
            bus.fire("gesture.smiling.start", base)

        if snapshot.smiling_released:
            bus.fire("gesture.smiling.end", base)

        return

    # Handle HandInputSnapshot
    base: Dict[str, Any] = {
        "hand": snapshot.handedness,
        "cursor_x": snapshot.cursor_x,
        "cursor_y": snapshot.cursor_y,
        "is_closed": snapshot.is_closed,
        "is_pinch": snapshot.is_pinch,
        "is_peace": snapshot.is_peace,
        "is_thumbs_up": snapshot.is_thumbs_up,
        "is_thumbs_down": snapshot.is_thumbs_down,
        "is_rock_sign": snapshot.is_rock_sign,
        "is_open_hand": snapshot.is_open_hand,
        "is_pointing": snapshot.is_pointing,
        "is_ok_sign": snapshot.is_ok_sign,
    }

    if snapshot.closed_pressed:
        bus.fire("gesture.closed.start", base)

    if snapshot.closed_released:
        bus.fire("gesture.closed.end", base)

    if snapshot.pinch_pressed:
        bus.fire("gesture.pinch.start", base)

    if snapshot.pinch_released:
        bus.fire("gesture.pinch.end", base)

    if snapshot.peace_pressed:
        bus.fire("gesture.peace.start", base)

    if snapshot.peace_released:
        bus.fire("gesture.peace.end", base)

    if snapshot.thumbs_up_pressed:
        bus.fire("gesture.thumbs_up.start", base)

    if snapshot.thumbs_up_released:
        bus.fire("gesture.thumbs_up.end", base)

    if snapshot.thumbs_down_pressed:
        bus.fire("gesture.thumbs_down.start", base)

    if snapshot.thumbs_down_released:
        bus.fire("gesture.thumbs_down.end", base)

    if snapshot.rock_sign_pressed:
        bus.fire("gesture.rock_sign.start", base)

    if snapshot.rock_sign_released:
        bus.fire("gesture.rock_sign.end", base)

    if snapshot.open_hand_pressed:
        bus.fire("gesture.open_hand.start", base)

    if snapshot.open_hand_released:
        bus.fire("gesture.open_hand.end", base)

    if snapshot.pointing_pressed:
        bus.fire("gesture.pointing.start", base)

    if snapshot.pointing_released:
        bus.fire("gesture.pointing.end", base)

    if snapshot.ok_sign_pressed:
        bus.fire("gesture.ok_sign.start", base)

    if snapshot.ok_sign_released:
        bus.fire("gesture.ok_sign.end", base)
