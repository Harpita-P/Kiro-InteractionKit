import cv2
import pygame
from typing import Tuple


def frame_to_surface(frame_bgr, size: Tuple[int, int]) -> pygame.Surface:
    """Convert an OpenCV BGR frame to a Pygame surface with the given size.

    Parameters
    ----------
    frame_bgr: np.ndarray
        BGR image from OpenCV.
    size: (width, height)
        Desired size of the resulting surface.
    """

    width, height = size
    frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
    frame_rgb = cv2.resize(frame_rgb, (width, height))
    return pygame.image.frombuffer(frame_rgb.tobytes(), (width, height), "RGB")


def draw_debug_camera(
    screen: pygame.Surface,
    frame_bgr,
    dest_rect: Tuple[int, int, int, int],
) -> None:
    """Draw the camera/debug view into the given region on the screen.

    Parameters
    ----------
    screen: pygame.Surface
        Target Pygame surface (typically the main screen).
    frame_bgr: np.ndarray
        BGR image from OpenCV (annotated frame from HandTracker).
    dest_rect: (x, y, width, height)
        Destination rectangle where the camera view should be drawn.
    """

    x, y, w, h = dest_rect
    surface = frame_to_surface(frame_bgr, (w, h))
    screen.blit(surface, (x, y))
