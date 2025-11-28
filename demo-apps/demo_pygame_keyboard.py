import os
import sys
from typing import List

import cv2
import pygame
import pyautogui

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
from kiro_motion_kit.mappings import keyboard_demo_mapping  # sets up mappings for this demo


WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 480
LEFT_WIDTH = WINDOW_WIDTH // 2
RIGHT_WIDTH = WINDOW_WIDTH - LEFT_WIDTH
FPS = 30

KEY_ROWS: List[str] = [
    "QWERTYUIOP",
    "ASDFGHJKL",
    "ZXCVBNM",
]
KEY_WIDTH = 50
KEY_HEIGHT = 50
KEY_MARGIN_X = 10
KEY_MARGIN_Y = 10
KEYBOARD_TOP = 50
KEYBOARD_LEFT = 50


class KeyButton:
    def __init__(self, rect: pygame.Rect, label: str) -> None:
        self.rect = rect
        self.label = label

    def draw(self, surface: pygame.Surface, font: pygame.font.Font, hovered: bool) -> None:
        base_color = (60, 60, 60)
        hover_color = (120, 120, 120)
        border_color = (200, 200, 200)

        color = hover_color if hovered else base_color
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, border_color, self.rect, 2)

        text_surf = font.render(self.label, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)


def build_keyboard() -> List[KeyButton]:
    keys: List[KeyButton] = []
    y = KEYBOARD_TOP
    for row in KEY_ROWS:
        row_width = len(row) * KEY_WIDTH + (len(row) - 1) * KEY_MARGIN_X
        x = KEYBOARD_LEFT + (LEFT_WIDTH - KEYBOARD_LEFT * 2 - row_width) // 2
        for ch in row:
            rect = pygame.Rect(x, y, KEY_WIDTH, KEY_HEIGHT)
            keys.append(KeyButton(rect, ch))
            x += KEY_WIDTH + KEY_MARGIN_X
        y += KEY_HEIGHT + KEY_MARGIN_Y
    return keys


def send_system_key(label: str) -> None:
    # Simple mapping: letters map directly, all sent as lowercase.
    pyautogui.press(label.lower())


def main() -> None:
    pygame.init()
    pyautogui.FAILSAFE = False  # avoid exceptions when moving near screen corners

    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Phantom Hands - On-Screen Keyboard")
    clock = pygame.time.Clock()

    font = pygame.font.SysFont(None, 28)

    # OpenCV camera
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Could not open webcam.")
        return

    hand_input = HandInputManager()
    keys = build_keyboard()

    # Event system and mappings
    bus = get_event_bus()

    # Start cursor roughly at center of left panel
    cursor_x = LEFT_WIDTH // 2
    cursor_y = WINDOW_HEIGHT // 2

    # Track which key is currently hovered so mapping can know what to type
    hovered_key_label = None

    SHOW_DEBUG_CAMERA = True

    # Map pinch.start to a generic game.key.type action; we will attach
    # the concrete key label in our listener.
    mapper.map_action(
        action="game.key.type",
        gesture_event="gesture.pinch.start",
    )

    def on_key_type(_data):
        if hovered_key_label:
            send_system_key(hovered_key_label)

    bus.on("game.key.type", on_key_type)

    try:
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            keys_pressed = pygame.key.get_pressed()
            if keys_pressed[pygame.K_ESCAPE]:
                running = False

            # Read and process frame
            success, frame = cap.read()
            if not success:
                print("Ignoring empty camera frame.")
                continue

            actions, annotated_frame = hand_input.update_from_frame(frame)
            dispatch_gesture_events(actions)

            # Map cursor position
            if (
                actions.is_present
                and actions.cursor_x is not None
                and actions.cursor_y is not None
            ):
                cursor_x = int(actions.cursor_x * LEFT_WIDTH)
                cursor_y = int(actions.cursor_y * WINDOW_HEIGHT)

            # Determine hovered key and remember its label for the
            # game.key.type handler.
            hovered_key = None
            hovered_key_label = None
            for key in keys:
                if key.rect.collidepoint(cursor_x, cursor_y):
                    hovered_key = key
                    hovered_key_label = key.label
                    break

            # Draw
            screen.fill((10, 10, 10))

            # Left: keyboard + cursor
            pygame.draw.rect(screen, (20, 20, 20), (0, 0, LEFT_WIDTH, WINDOW_HEIGHT))

            for key in keys:
                key.draw(screen, font, hovered=(key is hovered_key))

            # Draw cursor as small cyan circle
            pygame.draw.circle(screen, (0, 255, 255), (cursor_x, cursor_y), 8)

            # Right: camera (debug view)
            if SHOW_DEBUG_CAMERA and annotated_frame is not None:
                draw_debug_camera(
                    screen,
                    annotated_frame,
                    (LEFT_WIDTH, 0, RIGHT_WIDTH, WINDOW_HEIGHT),
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
