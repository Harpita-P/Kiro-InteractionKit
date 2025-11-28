from kiro_motion_kit import ActionMapper


# Mapping configuration for demo_pygame_keyboard.py
#
# Pinch start triggers a generic game.key.type action; the concrete
# key is decided in the demo based on which key is hovered.

_mapper = ActionMapper()

_mapper.map_action(
    action="game.key.type",
    gesture_event="gesture.pinch.start",
)
