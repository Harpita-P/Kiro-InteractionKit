#!/usr/bin/env python3
"""
Unit tests for UIManager class.
"""

import os
import sys
import pygame

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Import after path setup
sys.path.insert(0, os.path.join(PROJECT_ROOT, 'my_apps', 'Holo-Board'))
from main import UIManager


def test_ui_manager_initialization():
    """Test UIManager initialization."""
    pygame.init()
    
    screen_width = 1280
    screen_height = 720
    
    ui_manager = UIManager(screen_width, screen_height)
    
    # Check that assets are loaded
    assert ui_manager.record_button_image is not None
    assert ui_manager.vinyl_image is not None
    
    # Check button positioning (bottom-right corner)
    button_width = ui_manager.record_button_image.get_width()
    button_height = ui_manager.record_button_image.get_height()
    
    expected_button_x = screen_width - button_width - ui_manager.button_padding
    expected_button_y = screen_height - button_height - ui_manager.button_padding
    
    assert ui_manager.record_button_rect.x == expected_button_x
    assert ui_manager.record_button_rect.y == expected_button_y
    
    # Check vinyl positioning (top-right corner)
    vinyl_width = ui_manager.vinyl_image.get_width()
    
    expected_vinyl_x = screen_width - vinyl_width - ui_manager.vinyl_padding
    expected_vinyl_y = ui_manager.vinyl_padding
    
    assert ui_manager.vinyl_position[0] == expected_vinyl_x
    assert ui_manager.vinyl_position[1] == expected_vinyl_y
    
    # Check initial rotation
    assert ui_manager.vinyl_rotation == 0.0
    
    pygame.quit()
    print("✓ UIManager initialization test passed")


def test_button_click_detection():
    """Test button click detection with various mouse positions."""
    pygame.init()
    
    screen_width = 1280
    screen_height = 720
    
    ui_manager = UIManager(screen_width, screen_height)
    
    # Test click inside button
    button_center = ui_manager.record_button_rect.center
    assert ui_manager.is_button_clicked(button_center) == True
    
    # Test click at button top-left corner
    button_topleft = ui_manager.record_button_rect.topleft
    assert ui_manager.is_button_clicked(button_topleft) == True
    
    # Test click outside button (far left)
    assert ui_manager.is_button_clicked((0, 0)) == False
    
    # Test click outside button (near but not on button)
    outside_pos = (ui_manager.record_button_rect.x - 10, ui_manager.record_button_rect.y)
    assert ui_manager.is_button_clicked(outside_pos) == False
    
    pygame.quit()
    print("✓ Button click detection test passed")


def test_vinyl_rotation_update():
    """Test vinyl rotation angle increments."""
    pygame.init()
    
    ui_manager = UIManager(1280, 720)
    
    # Initial rotation should be 0
    assert ui_manager.vinyl_rotation == 0.0
    
    # Update rotation once (should increment by 2 degrees)
    ui_manager.update_vinyl_rotation()
    assert ui_manager.vinyl_rotation == 2.0
    
    # Update rotation multiple times
    for _ in range(10):
        ui_manager.update_vinyl_rotation()
    
    assert ui_manager.vinyl_rotation == 22.0  # 2 + 10*2 = 22
    
    # Test wraparound at 360 degrees
    ui_manager.vinyl_rotation = 359.0
    ui_manager.update_vinyl_rotation()
    assert ui_manager.vinyl_rotation == 1.0  # (359 + 2) % 360 = 1
    
    pygame.quit()
    print("✓ Vinyl rotation update test passed")


def test_ui_element_positioning():
    """Test UI element positioning for different screen sizes."""
    pygame.init()
    
    # Test with different screen sizes
    test_sizes = [
        (1280, 720),
        (1920, 1080),
        (640, 480)
    ]
    
    for width, height in test_sizes:
        ui_manager = UIManager(width, height)
        
        # Button should be in bottom-right corner
        button_right = ui_manager.record_button_rect.right
        button_bottom = ui_manager.record_button_rect.bottom
        
        assert button_right <= width
        assert button_bottom <= height
        # Button should be within padding distance from edges
        assert button_right >= width - ui_manager.record_button_image.get_width() - ui_manager.button_padding - 1
        assert button_bottom >= height - ui_manager.record_button_image.get_height() - ui_manager.button_padding - 1
        
        # Vinyl should be in top-right corner
        vinyl_x, vinyl_y = ui_manager.vinyl_position
        vinyl_width = ui_manager.vinyl_image.get_width()
        
        assert vinyl_x + vinyl_width <= width
        assert vinyl_y >= 0
        # Vinyl should be within padding distance from edges
        assert vinyl_x >= width - vinyl_width - ui_manager.vinyl_padding - 1
        assert vinyl_y <= ui_manager.vinyl_padding + 1
    
    pygame.quit()
    print("✓ UI element positioning test passed")


if __name__ == "__main__":
    print("Running UIManager unit tests...")
    print()
    
    test_ui_manager_initialization()
    test_button_click_detection()
    test_vinyl_rotation_update()
    test_ui_element_positioning()
    
    print()
    print("All UIManager tests passed! ✓")
