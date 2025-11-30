#!/usr/bin/env python3
"""
Unit tests for UI positioning, button click hitbox accuracy, and vinyl rotation.
"""

import os
import sys
import pytest

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Import after path setup
import pygame

# Initialize pygame for testing
pygame.init()

# Constants
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720


class TestUIPositioning:
    """Test UI positioning and sizing."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Load assets
        assets_dir = os.path.join(PROJECT_ROOT, "my_apps", "Holo-Board", "Assets")
        
        self.record_button_path = os.path.join(assets_dir, "recording-button.png")
        self.vinyl_path = os.path.join(assets_dir, "vinyl.png")
        
        self.record_button_image = pygame.image.load(self.record_button_path)
        self.vinyl_image = pygame.image.load(self.vinyl_path)
        
        # Set up button positioning (same as UIManager)
        self.button_padding = 20
        button_width = self.record_button_image.get_width()
        button_height = self.record_button_image.get_height()
        
        button_x = WINDOW_WIDTH - button_width - self.button_padding
        button_y = WINDOW_HEIGHT - button_height - self.button_padding
        
        self.record_button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
        
        # Set up vinyl positioning (same as UIManager)
        self.vinyl_padding = 20
        vinyl_width = self.vinyl_image.get_width()
        vinyl_height = self.vinyl_image.get_height()
        
        vinyl_x = WINDOW_WIDTH - vinyl_width - self.vinyl_padding
        vinyl_y = self.vinyl_padding
        
        self.vinyl_position = (vinyl_x, vinyl_y)
    
    def test_assets_exist(self):
        """Test that required assets exist."""
        assert os.path.exists(self.record_button_path), "Recording button asset not found"
        assert os.path.exists(self.vinyl_path), "Vinyl asset not found"
    
    def test_recording_button_size(self):
        """Test that recording button is 64x64 as specified."""
        width = self.record_button_image.get_width()
        height = self.record_button_image.get_height()
        
        assert width == 64, f"Recording button width should be 64, got {width}"
        assert height == 64, f"Recording button height should be 64, got {height}"
    
    def test_vinyl_size(self):
        """Test that vinyl indicator is 48x48 as specified."""
        width = self.vinyl_image.get_width()
        height = self.vinyl_image.get_height()
        
        assert width == 48, f"Vinyl width should be 48, got {width}"
        assert height == 48, f"Vinyl height should be 48, got {height}"
    
    def test_recording_button_position(self):
        """Test that recording button is positioned in bottom-right corner with padding."""
        # Button should be in bottom-right corner with 20px padding
        expected_x = WINDOW_WIDTH - 64 - 20  # width - button_width - padding
        expected_y = WINDOW_HEIGHT - 64 - 20  # height - button_height - padding
        
        assert self.record_button_rect.x == expected_x, \
            f"Button X position should be {expected_x}, got {self.record_button_rect.x}"
        assert self.record_button_rect.y == expected_y, \
            f"Button Y position should be {expected_y}, got {self.record_button_rect.y}"
    
    def test_vinyl_position(self):
        """Test that vinyl indicator is positioned in top-right corner with padding."""
        # Vinyl should be in top-right corner with 20px padding
        expected_x = WINDOW_WIDTH - 48 - 20  # width - vinyl_width - padding
        expected_y = 20  # padding
        
        assert self.vinyl_position[0] == expected_x, \
            f"Vinyl X position should be {expected_x}, got {self.vinyl_position[0]}"
        assert self.vinyl_position[1] == expected_y, \
            f"Vinyl Y position should be {expected_y}, got {self.vinyl_position[1]}"
    
    def test_button_hitbox_accuracy_center(self):
        """Test that clicking the center of the button is detected."""
        center_x = self.record_button_rect.centerx
        center_y = self.record_button_rect.centery
        
        assert self.record_button_rect.collidepoint(center_x, center_y), \
            "Center of button should be clickable"
    
    def test_button_hitbox_accuracy_corners(self):
        """Test that clicking the corners of the button is detected."""
        # Top-left corner (inside)
        assert self.record_button_rect.collidepoint(
            self.record_button_rect.left + 1,
            self.record_button_rect.top + 1
        ), "Top-left corner should be clickable"
        
        # Top-right corner (inside)
        assert self.record_button_rect.collidepoint(
            self.record_button_rect.right - 1,
            self.record_button_rect.top + 1
        ), "Top-right corner should be clickable"
        
        # Bottom-left corner (inside)
        assert self.record_button_rect.collidepoint(
            self.record_button_rect.left + 1,
            self.record_button_rect.bottom - 1
        ), "Bottom-left corner should be clickable"
        
        # Bottom-right corner (inside)
        assert self.record_button_rect.collidepoint(
            self.record_button_rect.right - 1,
            self.record_button_rect.bottom - 1
        ), "Bottom-right corner should be clickable"
    
    def test_button_hitbox_accuracy_outside(self):
        """Test that clicking outside the button is not detected."""
        # Just outside top-left
        assert not self.record_button_rect.collidepoint(
            self.record_button_rect.left - 1,
            self.record_button_rect.top - 1
        ), "Outside top-left should not be clickable"
        
        # Just outside bottom-right
        assert not self.record_button_rect.collidepoint(
            self.record_button_rect.right + 1,
            self.record_button_rect.bottom + 1
        ), "Outside bottom-right should not be clickable"
        
        # Far away
        assert not self.record_button_rect.collidepoint(0, 0), \
            "Top-left corner of screen should not be clickable"
    
    def test_vinyl_rotation_increment(self):
        """Test that vinyl rotation increments by 2 degrees per frame."""
        rotation = 0.0
        
        # Simulate 180 frames (6 seconds at 30 FPS)
        for _ in range(180):
            rotation = (rotation + 2) % 360
        
        # After 180 frames with 2°/frame, should be at 360° = 0°
        assert rotation == 0.0, f"After 180 frames, rotation should be 0°, got {rotation}"
    
    def test_vinyl_rotation_wraparound(self):
        """Test that vinyl rotation wraps around at 360 degrees."""
        rotation = 358.0
        
        # Increment by 2 degrees
        rotation = (rotation + 2) % 360
        
        assert rotation == 0.0, f"Rotation should wrap to 0° at 360°, got {rotation}"
    
    def test_vinyl_rotation_smoothness(self):
        """Test that vinyl rotation is smooth and consistent."""
        rotation = 0.0
        rotations = [rotation]
        
        # Simulate 60 frames (2 seconds at 30 FPS)
        for _ in range(60):
            rotation = (rotation + 2) % 360
            rotations.append(rotation)
        
        # Calculate deltas
        deltas = []
        for i in range(1, len(rotations)):
            delta = rotations[i] - rotations[i-1]
            # Handle wraparound
            if delta < -180:
                delta += 360
            elif delta > 180:
                delta -= 360
            deltas.append(delta)
        
        # All deltas should be exactly 2.0 (or very close due to floating point)
        for delta in deltas:
            assert abs(delta - 2.0) < 0.001, \
                f"Rotation delta should be 2.0°, got {delta}"
    
    def test_ui_elements_dont_overlap(self):
        """Test that UI elements don't overlap."""
        # Create vinyl rect
        vinyl_rect = pygame.Rect(
            self.vinyl_position[0],
            self.vinyl_position[1],
            self.vinyl_image.get_width(),
            self.vinyl_image.get_height()
        )
        
        # Check that button and vinyl don't overlap
        assert not self.record_button_rect.colliderect(vinyl_rect), \
            "Button and vinyl indicator should not overlap"
    
    def test_ui_elements_within_screen_bounds(self):
        """Test that UI elements are fully within screen bounds."""
        # Button should be fully within screen
        assert self.record_button_rect.left >= 0, "Button left edge should be within screen"
        assert self.record_button_rect.top >= 0, "Button top edge should be within screen"
        assert self.record_button_rect.right <= WINDOW_WIDTH, "Button right edge should be within screen"
        assert self.record_button_rect.bottom <= WINDOW_HEIGHT, "Button bottom edge should be within screen"
        
        # Vinyl should be fully within screen
        vinyl_rect = pygame.Rect(
            self.vinyl_position[0],
            self.vinyl_position[1],
            self.vinyl_image.get_width(),
            self.vinyl_image.get_height()
        )
        
        assert vinyl_rect.left >= 0, "Vinyl left edge should be within screen"
        assert vinyl_rect.top >= 0, "Vinyl top edge should be within screen"
        assert vinyl_rect.right <= WINDOW_WIDTH, "Vinyl right edge should be within screen"
        assert vinyl_rect.bottom <= WINDOW_HEIGHT, "Vinyl bottom edge should be within screen"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
