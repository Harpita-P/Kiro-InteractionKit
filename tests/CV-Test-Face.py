#!/usr/bin/env python3
"""
CV-Test-Face: Face Gesture Testing Demo

A simple interactive demo to test all face gestures with visual feedback.
Control a shape's properties using facial expressions:
- Blink: Toggle between circle and triangle
- Mouth Open: Change shape size
- Smiling: Change shape color to yellow
"""

import os
import sys
import cv2
import pygame

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from kiro_motion_magic.controllers.face_controller import FaceTracker

# Constants
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 600
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
FPS = 30

# Minimalist color scheme (Apple-style, professional)
BG_COLOR = (248, 248, 248)
TEXT_PRIMARY = (28, 28, 30)
TEXT_SECONDARY = (142, 142, 147)
ACCENT_PRIMARY = (0, 122, 255)
ACCENT_YELLOW = (255, 204, 0)
ACCENT_GREEN = (52, 199, 89)
BORDER_COLOR = (200, 200, 200)


class FaceGestureDemo:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Face Gesture Demo")
        self.clock = pygame.time.Clock()

        # Camera and tracker
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)
        self.tracker = FaceTracker()

        # Shape properties
        self.shape_x = WINDOW_WIDTH - 300
        self.shape_y = WINDOW_HEIGHT // 2
        self.shape_size = 50
        self.shape_color = ACCENT_PRIMARY
        self.is_triangle = False  # False = circle, True = triangle

        # Blink detection state
        self.prev_blink = False
        self.blink_cooldown = 0

        self.active_gestures = []

    def process_gestures(self, state):
        self.active_gestures = []
        if not state.is_present:
            return

        # Decrease cooldown
        if self.blink_cooldown > 0:
            self.blink_cooldown -= 1

        # Blink - Toggle shape (with cooldown to prevent rapid toggling)
        current_blink = state.is_blink
        if current_blink and not self.prev_blink and self.blink_cooldown == 0:
            self.active_gestures.append("Blink")
            self.is_triangle = not self.is_triangle
            self.blink_cooldown = 15  # ~0.5 seconds at 30 FPS
        self.prev_blink = current_blink

        # Mouth Open - Increase size
        if state.is_mouth_open:
            self.active_gestures.append("Mouth Open")
            self.shape_size = min(150, self.shape_size + 2)
        else:
            # Shrink back when mouth closed
            if self.shape_size > 50:
                self.shape_size = max(50, self.shape_size - 1)

        # Smiling - Yellow color
        if state.is_smiling:
            self.active_gestures.append("Smiling")
            self.shape_color = ACCENT_YELLOW
        else:
            # Reset to primary when not smiling
            self.shape_color = ACCENT_PRIMARY

    def draw_camera_feed(self, frame):
        camera_y = (WINDOW_HEIGHT - CAMERA_HEIGHT) // 2

        # thin border only
        border_rect = pygame.Rect(
            10, camera_y - 1, CAMERA_WIDTH + 2, CAMERA_HEIGHT + 2
        )
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
        title = font_large.render("Face Gesture Demo", True, TEXT_PRIMARY)
        self.screen.blit(title, (CAMERA_WIDTH + 60, 40))

        # Minimal instructions
        instructions = [
            "Blink — Toggle Shape",
            "Mouth Open — Size",
            "Smiling — Yellow Color",
        ]

        y = 120
        for item in instructions:
            text = font_small.render(item, True, TEXT_SECONDARY)
            self.screen.blit(text, (CAMERA_WIDTH + 60, y))
            y += 28

        # Shape status
        shape_name = "Triangle" if self.is_triangle else "Circle"
        status_text = font_small.render(
            f"Shape: {shape_name}", True, TEXT_SECONDARY
        )
        self.screen.blit(status_text, (CAMERA_WIDTH + 60, y + 10))

        # Active gestures as one line
        if self.active_gestures:
            active_text = ", ".join(self.active_gestures)
            gesture_text = font_medium.render(active_text, True, ACCENT_PRIMARY)
            self.screen.blit(
                gesture_text, (CAMERA_WIDTH + 60, WINDOW_HEIGHT - 70)
            )

        # Footer
        footer = font_small.render("ESC to exit", True, TEXT_SECONDARY)
        self.screen.blit(footer, (WINDOW_WIDTH - 140, WINDOW_HEIGHT - 40))

    def draw_shape(self):
        if self.is_triangle:
            # Draw triangle
            half_size = int(self.shape_size)
            points = [
                (int(self.shape_x), int(self.shape_y - half_size)),  # top
                (int(self.shape_x - half_size), int(self.shape_y + half_size)),  # bottom left
                (int(self.shape_x + half_size), int(self.shape_y + half_size)),  # bottom right
            ]
            pygame.draw.polygon(self.screen, self.shape_color, points)
        else:
            # Draw circle
            pygame.draw.circle(
                self.screen,
                self.shape_color,
                (int(self.shape_x), int(self.shape_y)),
                int(self.shape_size),
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
            self.draw_shape()

            pygame.display.flip()
            self.clock.tick(FPS)

        self.cap.release()
        self.tracker.close()
        pygame.quit()


def main():
    demo = FaceGestureDemo()
    demo.run()


if __name__ == "__main__":
    main()
