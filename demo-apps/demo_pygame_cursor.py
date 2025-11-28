import os
import sys

import cv2
import pygame

# Ensure the project root (parent of demo-apps) is on sys.path so that
# the kiro_motion_kit package can be imported whether this script is run
# from the project root or from the demo-apps folder.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from kiro_motion_kit import (
    HandInputManager,
    dispatch_gesture_events,
    get_event_bus,
)
from kiro_motion_kit.debug_view import draw_debug_camera
from kiro_motion_kit.mappings import cursor_demo_mapping  # sets up mappings for this demo


WINDOW_WIDTH = 1600
WINDOW_HEIGHT = 900
LEFT_WIDTH = WINDOW_WIDTH // 2
RIGHT_WIDTH = WINDOW_WIDTH - LEFT_WIDTH
FPS = 30


def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption(" Pygame Cursor Demo")
    clock = pygame.time.Clock()

    # OpenCV camera
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Could not open webcam.")
        return

    hand_input = HandInputManager()

    # Event system and mappings
    bus = get_event_bus()

    # Start circle roughly at center of the window
    circle_x = WINDOW_WIDTH // 2
    circle_y = WINDOW_HEIGHT // 2

    # Game logic state for the circle (separate from hand tracking logic)
    circle_radius = 20
    base_radius = 20
    max_radius = 60
    radius_growth_speed = 8  # pixels per frame when growing/shrinking
    circle_color = (200, 50, 50)  # red by default

    # Circle behavior flags driven by game.* events
    grow_active = False

    def on_grow_start(_data):
        nonlocal grow_active
        grow_active = True

    def on_grow_end(_data):
        nonlocal grow_active
        grow_active = False

    def on_color_green(_data):
        nonlocal circle_color
        circle_color = (50, 200, 50)

    def on_color_red(_data):
        nonlocal circle_color
        circle_color = (200, 50, 50)

    bus.on("game.circle.grow.start", on_grow_start)
    bus.on("game.circle.grow.end", on_grow_end)
    bus.on("game.circle.color.green", on_color_green)
    bus.on("game.circle.color.red", on_color_red)

    SHOW_DEBUG_CAMERA = True

    try:
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            # ESC key to quit
            keys = pygame.key.get_pressed()
            if keys[pygame.K_ESCAPE]:
                running = False

            # Read and process a frame via the hand input adapter
            success, frame = cap.read()
            if not success:
                print("Ignoring empty camera frame.")
                continue

            actions, annotated_frame = hand_input.update_from_frame(frame)
            dispatch_gesture_events(actions)

            # Map normalized cursor position to full window if hand present
            if (
                actions.is_present
                and actions.cursor_x is not None
                and actions.cursor_y is not None
            ):
                circle_x = int(actions.cursor_x * WINDOW_WIDTH)
                circle_y = int(actions.cursor_y * WINDOW_HEIGHT)

            # -------------------------
            # Game logic driven by game.* actions
            # -------------------------
            # 1) Size animation: grow when grow_active, shrink back otherwise.
            target_radius = max_radius if grow_active else base_radius
            if circle_radius < target_radius:
                circle_radius = min(circle_radius + radius_growth_speed, target_radius)
            elif circle_radius > target_radius:
                circle_radius = max(circle_radius - radius_growth_speed, target_radius)

            # 2) Color change is handled via game.circle.color.* events

            # Clear screen
            screen.fill((30, 30, 30))

            # Draw game area: circle controlled by hand cursor and
            # animated/colored according to gestures.
            pygame.draw.rect(screen, (20, 20, 20), (0, 0, WINDOW_WIDTH, WINDOW_HEIGHT))
            pygame.draw.circle(screen, circle_color, (circle_x, circle_y), circle_radius)

            # Draw camera view as a smaller overlay in the bottom-right corner
            if SHOW_DEBUG_CAMERA and annotated_frame is not None:
                overlay_width = 320
                overlay_height = 240
                overlay_x = WINDOW_WIDTH - overlay_width - 16
                overlay_y = WINDOW_HEIGHT - overlay_height - 16
                draw_debug_camera(
                    screen,
                    annotated_frame,
                    (overlay_x, overlay_y, overlay_width, overlay_height),
                )

            pygame.display.flip()
            clock.tick(FPS)

    finally:
        cap.release()
        hand_input.close()
        pygame.quit()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pygame.quit()
        sys.exit(0)
