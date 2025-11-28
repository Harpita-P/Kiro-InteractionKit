from typing import Any, Callable, Dict, Optional

from .events.event_bus import get_event_bus


class ActionMapper:
    """Helper to map gesture.* events to higher-level game.* actions.

    Typical usage in a game-specific file, e.g. game_mapping.py:

        from kiro_motion_kit import ActionMapper

        mapper = ActionMapper()
        mapper.map_action(
            action="game.jump",
            gesture_event="gesture.pinch.start",
            hand="Right",
        )

    Then, elsewhere in the game, listen for "game.jump" on the EventBus.
    """

    def __init__(self) -> None:
        self._bus = get_event_bus()

    def map_action(
        self,
        *,
        action: str,
        gesture_event: str,
        hand: Optional[str] = None,
        predicate: Optional[Callable[[Dict[str, Any]], bool]] = None,
    ) -> None:
        """Map a gesture_event to a game action.

        Parameters
        ----------
        action: str
            Name of the game-level action event to emit, e.g. "game.jump".
        gesture_event: str
            Name of the gesture event to listen to, e.g. "gesture.pinch.start".
        hand: Optional[str]
            Optional handedness filter (e.g. "Right", "Left"). If provided,
            only events whose data["hand"] matches (case-insensitive) will
            trigger the action.
        predicate: Optional[Callable[[Dict[str, Any]], bool]]
            Optional extra filter for advanced matching using the event payload.
        """

        def _listener(data: Dict[str, Any]) -> None:
            if hand is not None:
                event_hand = data.get("hand")
                if not event_hand or event_hand.lower() != hand.lower():
                    return

            if predicate is not None and not predicate(data):
                return

            self._bus.fire(action, data)

        self._bus.on(gesture_event, _listener)
