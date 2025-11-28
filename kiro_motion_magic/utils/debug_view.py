"""Debug view utilities for rendering camera feed in Pygame."""

import cv2
import pygame


def draw_debug_camera(screen, frame_bgr, rect):
    """Draw camera feed on pygame surface.
    
    Args:
        screen: Pygame surface to draw on
        frame_bgr: OpenCV BGR frame
        rect: Tuple of (x, y, width, height) for camera position
    """
    x, y, width, height = rect
    
    # Convert BGR to RGB and resize
    frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
    frame_rgb = cv2.resize(frame_rgb, (width, height))
    
    # Create pygame surface and draw
    frame_surface = pygame.surfarray.make_surface(frame_rgb.swapaxes(0, 1))
    screen.blit(frame_surface, (x, y))
