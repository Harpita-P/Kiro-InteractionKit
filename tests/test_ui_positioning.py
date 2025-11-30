#!/usr/bin/env python3
"""
Test UI positioning, button click hitbox accuracy, and vinyl rotation smoothness.
"""

import os
import sys
import pygame

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Constants
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
FPS = 30

# Test colors
BG_COLOR = (40, 40, 40)
HITBOX_COLOR = (255, 0, 0, 100)  # Semi-transparent red
TEXT_COLOR = (255, 255, 255)
CLICK_INDICATOR_COLOR = (0, 255, 0)


class UIPositioningTest:
    """Test UI positioning and interaction."""
    
    def __init__(self):
        """Initialize the test."""
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("UI Positioning Test - Holo-Board")
        self.clock = pygame.time.Clock()
        
        # Load assets
        assets_dir = os.path.join(PROJECT_ROOT, "my_apps", "Holo-Board", "Assets")
        
        # Load record button asset
        record_button_path = os.path.join(assets_dir, "recording-button.png")
        self.record_button_image = pygame.image.load(record_button_path)
        
        # Load vinyl indicator asset
        vinyl_path = os.path.join(assets_dir, "vinyl.png")
        self.vinyl_image = pygame.image.load(vinyl_path)
        
        # Record button positioning (bottom-right corner with padding)
        self.button_padding = 20
        button_width = self.record_button_image.get_width()
        button_height = self.record_button_image.get_height()
        
        button_x = WINDOW_WIDTH - button_width - self.button_padding
        button_y = WINDOW_HEIGHT - button_height - self.button_padding
        
        self.record_button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
        
        # Vinyl indicator positioning (top-right corner with padding)
        self.vinyl_padding = 20
        vinyl_width = self.vinyl_image.get_width()
        vinyl_height = self.vinyl_image.get_height()
        
        vinyl_x = WINDOW_WIDTH - vinyl_width - self.vinyl_padding
        vinyl_y = self.vinyl_padding
        
        self.vinyl_position = (vinyl_x, vinyl_y)
        
        # Vinyl rotation state
        self.vinyl_rotation = 0.0
        
        # Click tracking
        self.last_click_pos = None
        self.click_timer = 0
        self.click_was_inside = False
        
        # Rotation tracking for smoothness test
        self.rotation_history = []
        self.max_history = 60  # Track last 60 frames (2 seconds at 30 FPS)
        
        print(f"UI Positioning Test initialized")
        print(f"Window: {WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        print(f"Record button: {button_width}x{button_height} at ({button_x}, {button_y})")
        print(f"Vinyl indicator: {vinyl_width}x{vinyl_height} at {self.vinyl_position}")
        print(f"\nInstructions:")
        print(f"  - Click anywhere to test button hitbox accuracy")
        print(f"  - Green = click inside button hitbox")
        print(f"  - Red = click outside button hitbox")
        print(f"  - Vinyl rotates continuously to test smoothness")
        print(f"  - Press ESC to exit")
    
    def is_button_clicked(self, mouse_pos):
        """
        Check if the record button was clicked.
        
        Args:
            mouse_pos: Tuple (x, y) of mouse position
            
        Returns:
            Boolean indicating if button was clicked
        """
        return self.record_button_rect.collidepoint(mouse_pos)
    
    def handle_events(self):
        """Process events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Track click position
                mouse_pos = pygame.mouse.get_pos()
                self.last_click_pos = mouse_pos
                self.click_timer = 60  # Show for 2 seconds (60 frames at 30 FPS)
                self.click_was_inside = self.is_button_clicked(mouse_pos)
                
                if self.click_was_inside:
                    print(f"✓ Click inside button hitbox at {mouse_pos}")
                else:
                    print(f"✗ Click outside button hitbox at {mouse_pos}")
        return True
    
    def update(self):
        """Update state."""
        # Update vinyl rotation (2 degrees per frame as per design)
        self.vinyl_rotation = (self.vinyl_rotation + 2) % 360
        
        # Track rotation for smoothness analysis
        self.rotation_history.append(self.vinyl_rotation)
        if len(self.rotation_history) > self.max_history:
            self.rotation_history.pop(0)
        
        # Decrement click timer
        if self.click_timer > 0:
            self.click_timer -= 1
    
    def draw_vinyl_indicator(self):
        """Render the spinning vinyl indicator."""
        # Rotate the vinyl image
        rotated_vinyl = pygame.transform.rotate(self.vinyl_image, self.vinyl_rotation)
        
        # Get the rect of the rotated image (centered on original position)
        rotated_rect = rotated_vinyl.get_rect(center=(
            self.vinyl_position[0] + self.vinyl_image.get_width() // 2,
            self.vinyl_position[1] + self.vinyl_image.get_height() // 2
        ))
        
        # Draw the rotated vinyl
        self.screen.blit(rotated_vinyl, rotated_rect.topleft)
    
    def render(self):
        """Render test UI."""
        # Clear screen
        self.screen.fill(BG_COLOR)
        
        # Draw record button
        self.screen.blit(self.record_button_image, self.record_button_rect.topleft)
        
        # Draw button hitbox outline
        pygame.draw.rect(self.screen, (255, 255, 0), self.record_button_rect, 2)
        
        # Draw vinyl indicator
        self.draw_vinyl_indicator()
        
        # Draw vinyl hitbox outline
        vinyl_rect = pygame.Rect(
            self.vinyl_position[0],
            self.vinyl_position[1],
            self.vinyl_image.get_width(),
            self.vinyl_image.get_height()
        )
        pygame.draw.rect(self.screen, (255, 255, 0), vinyl_rect, 2)
        
        # Draw click indicator if recent click
        if self.click_timer > 0 and self.last_click_pos is not None:
            color = CLICK_INDICATOR_COLOR if self.click_was_inside else (255, 0, 0)
            pygame.draw.circle(self.screen, color, self.last_click_pos, 10, 3)
            
            # Draw line from click to button center
            button_center = self.record_button_rect.center
            pygame.draw.line(self.screen, color, self.last_click_pos, button_center, 1)
        
        # Draw info text
        font = pygame.font.Font(None, 24)
        
        # Title
        title = font.render("UI Positioning Test - Holo-Board", True, TEXT_COLOR)
        self.screen.blit(title, (20, 20))
        
        # Instructions
        instructions = [
            "Click anywhere to test button hitbox accuracy",
            "Green = inside hitbox, Red = outside hitbox",
            "Vinyl rotates at 2°/frame for smoothness test",
            "Press ESC to exit"
        ]
        
        y = 60
        for line in instructions:
            text = font.render(line, True, TEXT_COLOR)
            self.screen.blit(text, (20, y))
            y += 30
        
        # Rotation info
        rotation_text = font.render(f"Vinyl rotation: {self.vinyl_rotation:.1f}°", True, TEXT_COLOR)
        self.screen.blit(rotation_text, (20, WINDOW_HEIGHT - 60))
        
        # Smoothness analysis
        if len(self.rotation_history) >= 2:
            # Calculate rotation deltas
            deltas = []
            for i in range(1, len(self.rotation_history)):
                delta = self.rotation_history[i] - self.rotation_history[i-1]
                # Handle wraparound at 360°
                if delta < -180:
                    delta += 360
                elif delta > 180:
                    delta -= 360
                deltas.append(delta)
            
            # Check if rotation is smooth (should be consistently 2°)
            if deltas:
                avg_delta = sum(deltas) / len(deltas)
                smoothness_text = font.render(f"Avg rotation delta: {avg_delta:.2f}°/frame (expected: 2.00)", True, TEXT_COLOR)
                self.screen.blit(smoothness_text, (20, WINDOW_HEIGHT - 30))
        
        pygame.display.flip()
    
    def run(self):
        """Main test loop."""
        running = True
        
        while running:
            running = self.handle_events()
            self.update()
            self.render()
            self.clock.tick(FPS)
        
        # Print summary
        print("\n=== Test Summary ===")
        print(f"Record button size: {self.record_button_image.get_width()}x{self.record_button_image.get_height()}")
        print(f"Record button position: {self.record_button_rect.topleft}")
        print(f"Vinyl size: {self.vinyl_image.get_width()}x{self.vinyl_image.get_height()}")
        print(f"Vinyl position: {self.vinyl_position}")
        
        if len(self.rotation_history) >= 2:
            deltas = []
            for i in range(1, len(self.rotation_history)):
                delta = self.rotation_history[i] - self.rotation_history[i-1]
                if delta < -180:
                    delta += 360
                elif delta > 180:
                    delta -= 360
                deltas.append(delta)
            
            if deltas:
                avg_delta = sum(deltas) / len(deltas)
                print(f"Average rotation delta: {avg_delta:.2f}°/frame (expected: 2.00)")
                
                # Check smoothness
                if abs(avg_delta - 2.0) < 0.1:
                    print("✓ Vinyl rotation is smooth and consistent")
                else:
                    print("✗ Vinyl rotation may have issues")
        
        pygame.quit()


def main():
    """Entry point."""
    test = UIPositioningTest()
    test.run()


if __name__ == "__main__":
    main()
