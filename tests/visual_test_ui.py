#!/usr/bin/env python3
"""
Visual test for UIManager - displays UI elements for manual verification.
Press SPACE to toggle vinyl indicator visibility.
Press ESC to exit.
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

# Constants
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
FPS = 30


def main():
    """Run visual test for UIManager."""
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("UIManager Visual Test")
    clock = pygame.time.Clock()
    
    # Initialize UIManager
    ui_manager = UIManager(WINDOW_WIDTH, WINDOW_HEIGHT)
    
    # State
    show_vinyl = False
    running = True
    
    print("UIManager Visual Test")
    print("- Record button should appear in bottom-right corner")
    print("- Press SPACE to toggle vinyl indicator (simulates recording)")
    print("- Click the record button to test click detection")
    print("- Press ESC to exit")
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    show_vinyl = not show_vinyl
                    print(f"Vinyl indicator: {'ON' if show_vinyl else 'OFF'}")
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if ui_manager.is_button_clicked(mouse_pos):
                    print("✓ Record button clicked!")
                    show_vinyl = not show_vinyl
        
        # Clear screen with a gray background
        screen.fill((50, 50, 50))
        
        # Draw UI elements
        ui_manager.draw_record_button(screen)
        
        if show_vinyl:
            ui_manager.update_vinyl_rotation()
            ui_manager.draw_vinyl_indicator(screen)
        
        # Draw instructions
        font = pygame.font.Font(None, 36)
        instructions = [
            "UIManager Visual Test",
            "",
            "SPACE - Toggle vinyl indicator",
            "Click button - Test click detection",
            "ESC - Exit"
        ]
        
        y = 50
        for line in instructions:
            text = font.render(line, True, (255, 255, 255))
            screen.blit(text, (50, y))
            y += 40
        
        # Show vinyl status
        status_text = f"Vinyl: {'VISIBLE (Recording)' if show_vinyl else 'HIDDEN'}"
        status_surface = font.render(status_text, True, (0, 255, 0) if show_vinyl else (255, 100, 100))
        screen.blit(status_surface, (50, WINDOW_HEIGHT - 100))
        
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()
    print("Visual test complete!")


if __name__ == "__main__":
    main()
