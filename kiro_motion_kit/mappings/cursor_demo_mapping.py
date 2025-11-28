from kiro_motion_kit import ActionMapper


# Mapping configuration for demo_pygame_cursor.py
#
# Circle grows when the hand closes, returns to normal when it opens.
# Circle turns green when pinching, red when released.

_mapper = ActionMapper()

_mapper.map_action(
    action="game.circle.grow.start",
    gesture_event="gesture.closed.start",
)

_mapper.map_action(
    action="game.circle.grow.end",
    gesture_event="gesture.closed.end",
)

_mapper.map_action(
    action="game.circle.color.green",
    gesture_event="gesture.rock_sign.start",
)

_mapper.map_action(
    action="game.circle.color.red",
    gesture_event="gesture.rock_sign.end",
)
