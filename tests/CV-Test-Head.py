#!/usr/bin/env python3
"""
CV-Test-Head: Head Gesture Testing Demo

A simple interactive demo to test all head gestures with visual feedback.
Control a circle's properties using head movements:
- Nod Up/Down: Change circle size
- Turn Left/Right: Change circle color (red/blue)
- Tilt Left/Right: Move circle position
"""

import os
import sys
import cv2
import pygame

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from kiro_interaction_kit.controllers.head_controller import HeadTracker
from kiro_interaction_kit.gestures.head_gestures import (
    is_nod_up,
    is_nod_down,
    is_turn_left,
    is_turn_right,
    is_tilt_left,
    is_tilt_right,
)

# Constants
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 600
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
FPS = 30

# Minimalist color scheme (Apple-style, professional)
BG_COLOR        = (248, 248, 248)
TEXT_PRIMARY    = (28, 28, 30)
TEXT_SECONDARY  = (142, 142, 147)
ACCENT_PRIMARY  = (0, 122, 255)
ACCENT_RED      = (255, 69, 58)
ACCENT_BLUE     = (0, 122, 255)
BORDER_COLOR    = (200, 200, 200)


class HeadGestureDemo:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Head Gesture Demo")
        self.clock = pygame.time.Clock()

        # Camera and tracker
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)
        self.tracker = HeadTracker()

        # Circle properties
        self.circle_x = WINDOW_WIDTH - 300
        self.circle_y = WINDOW_HEIGHT // 2
        self.circle_radius = 50
        self.circle_color = ACCENT_PRIMARY

        self.active_gestures = []

    def process_gestures(self, state):
        self.active_gestures = []
        if not state.is_present:
            return

        if is_nod_up(state.x_axis):
            self.active_gestures.append("Nod Up")
            self.circle_radius = min(150, self.circle_radius + 2)

        if is_nod_down(state.x_axis):
            self.active_gestures.append("Nod Down")
            self.circle_radius = max(20, self.circle_radius - 2)

        if is_turn_left(state.y_axis):
            self.active_gestures.append("Turn Left")
            self.circle_color = ACCENT_RED

        if is_turn_right(state.y_axis):
            self.active_gestures.append("Turn Right")
            self.circle_color = ACCENT_BLUE

        if is_tilt_left(state.z_axis):
            self.active_gestures.append("Tilt Left")
            self.circle_x = max(CAMERA_WIDTH + 50, self.circle_x - 3)

        if is_tilt_right(state.z_axis):
            self.active_gestures.append("Tilt Right")
            self.circle_x = min(WINDOW_WIDTH - 50, self.circle_x + 3)

        # Default color if no turn gestures
        if not any(g in self.active_gestures for g in ["Turn Left", "Turn Right"]):
            self.circle_color = ACCENT_PRIMARY

    def draw_camera_feed(self, frame):
        camera_y = (WINDOW_HEIGHT - CAMERA_HEIGHT) // 2

        # thin border only — no shadows
        border_rect = pygame.Rect(10, camera_y - 1, CAMERA_WIDTH + 2, CAMERA_HEIGHT + 2)
        pygame.draw.rect(self.screen, BORDER_COLOR, border_rect, 1)

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_rgb = cv2.resize(frame_rgb, (CAMERA_WIDTH, CAMERA_HEIGHT))
        frame_surface = pygame.surfarray.make_surface(frame_rgb.swapaxes(0, 1))
        self.screen.blit(frame_surface, (11, camera_y))

    def draw_ui(self):
        font_large = pygame.font.Font(None, 44)
        font_medium = pygame.font.Font(None, 30)
        font_small = pygame.font.Font(None, 24)

        # Title
        title = font_large.render("Head Gesture Demo", True, TEXT_PRIMARY)
        self.screen.blit(title, (CAMERA_WIDTH + 60, 40))

        # Minimal instructions
        instructions = [
            "Nod Up / Down — Size",
            "Turn Left / Right — Color",
            "Tilt Left / Right — Position",
        ]

        y = 120
        for item in instructions:
            text = font_small.render(item, True, TEXT_SECONDARY)
            self.screen.blit(text, (CAMERA_WIDTH + 60, y))
            y += 28

        # Active gestures as one line
        if self.active_gestures:
            active_text = ", ".join(self.active_gestures)
            gesture_text = font_medium.render(active_text, True, ACCENT_PRIMARY)
            self.screen.blit(gesture_text, (CAMERA_WIDTH + 60, WINDOW_HEIGHT - 70))

        # Footer
        footer = font_small.render("ESC to exit", True, TEXT_SECONDARY)
        self.screen.blit(footer, (WINDOW_WIDTH - 140, WINDOW_HEIGHT - 40))

    def draw_circle(self):
        pygame.draw.circle(
            self.screen,
            self.circle_color,
            (int(self.circle_x), int(self.circle_y)),
            int(self.circle_radius)
        )

    def run(self):
        running = True

        while running:
            # events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False

            success, frame = self.cap.read()
            if not success:
                print("Failed to read camera.")
                break

            annotated_frame, state = self.tracker.process_frame(frame)
            self.process_gestures(state)

            self.screen.fill(BG_COLOR)
            self.draw_camera_feed(annotated_frame)
            self.draw_ui()
            self.draw_circle()

            pygame.display.flip()
            self.clock.tick(FPS)

        self.cap.release()
        self.tracker.close()
        pygame.quit()


def main():
    demo = HeadGestureDemo()
    demo.run()


if __name__ == "__main__":
    main()
