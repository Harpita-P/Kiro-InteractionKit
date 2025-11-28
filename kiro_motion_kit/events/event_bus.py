from collections import defaultdict
from typing import Any, Callable, Dict, List


EventCallback = Callable[[Dict[str, Any]], None]


class EventBus:
    """Simple pub/sub event bus.

    - on(event, callback): subscribe
    - off(event, callback): unsubscribe
    - fire(event, data): publish

    All payloads are plain dictionaries for simplicity.
    """

    def __init__(self) -> None:
        self._subscribers: Dict[str, List[EventCallback]] = defaultdict(list)

    def on(self, event_name: str, callback: EventCallback) -> None:
        self._subscribers[event_name].append(callback)

    def off(self, event_name: str, callback: EventCallback) -> None:
        if event_name not in self._subscribers:
            return
        lst = self._subscribers[event_name]
        if callback in lst:
            lst.remove(callback)

    def fire(self, event_name: str, data: Dict[str, Any] | None = None) -> None:
        if data is None:
            data = {}
        for callback in list(self._subscribers.get(event_name, [])):
            callback(data)


# Shared singleton instance that most apps will use
_global_bus = EventBus()


def get_event_bus() -> EventBus:
    """Return the global event bus instance."""

    return _global_bus
