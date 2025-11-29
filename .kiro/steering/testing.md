# Testing Guidelines

## Creating CV Test Demos

When a user requests to test gestures (hand, head, or face), create a simple interactive demo following this pattern:

### Naming Convention
- **Hand gestures**: `tests/CV-Test-Hands.py`
- **Head gestures**: `tests/CV-Test-Head.py`
- **Face gestures**: `tests/CV-Test-Face.py`

**Important**: All test files must be created in the `tests/` folder, not in `demo-apps/`.

### UI Design Pattern (Minimalist Apple-Style)

Use this exact design system for all CV test demos:

#### Color Scheme
```python
# Minimalist color scheme (Apple-style, professional)
BG_COLOR        = (248, 248, 248)  # Very light gray background
TEXT_PRIMARY    = (28, 28, 30)     # Dark text
TEXT_SECONDARY  = (142, 142, 147)  # Light gray text
ACCENT_PRIMARY  = (0, 122, 255)    # iOS blue
ACCENT_RED      = (255, 69, 58)    # Modern red
ACCENT_BLUE     = (0, 122, 255)    # iOS blue
BORDER_COLOR    = (200, 200, 200)  # Light border
```

#### Layout Structure
- **Window size**: 1200x600
- **Camera feed**: Left side (640x480) with thin 1px border, no shadows
- **Interactive element**: Circle on right side that responds to gestures
- **Instructions**: Simple text list, no cards
- **Active gestures**: Comma-separated list at bottom
- **Footer**: "ESC to exit" in bottom right

#### Design Principles
- **Flat design**: No shadows, no gradients, no card backgrounds
- **Thin borders**: 1px borders only where needed
- **Minimal text**: Short, clear instructions
- **Clean typography**: Use pygame default fonts with appropriate sizes
  - Title: 44pt
  - Active gestures: 30pt
  - Instructions/Footer: 24pt
- **Camera annotations**: Show landmarks and tracking data on camera feed
- **Drawing order**: Background → Camera → UI → Interactive element (on top)

### Demo Structure

Each CV test demo should include:

1. **Camera feed with annotations**: Show tracking landmarks/data
2. **Interactive element**: Circle that responds to gestures
3. **Gesture mappings**: Each gesture controls a different property
   - Size (increase/decrease)
   - Color (change between colors)
   - Position (move left/right or up/down)
4. **Visual feedback**: Display active gestures in real-time
5. **Simple instructions**: Clear gesture → action mapping

### Example Gesture Mappings

**Head Gestures:**
- Nod Up/Down → Size
- Turn Left/Right → Color
- Tilt Left/Right → Position

**Hand Gestures:**
- Fist/Open Hand → Size
- Pinch/Peace → Color
- Pointing Left/Right → Position

**Face Gestures:**
- Blink → Toggle property
- Mouth Open → Size
- Smile → Color

### Code Template

```python
#!/usr/bin/env python3
"""
CV-Test-[Type]: [Type] Gesture Testing Demo

A simple interactive demo to test all [type] gestures with visual feedback.
"""

import os
import sys
import cv2
import pygame

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from kiro_interaction_kit.controllers.[type]_controller import [Type]Tracker
from kiro_interaction_kit.gestures.[type]_gestures import (
    # Import gesture detection functions
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

class [Type]GestureDemo:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("[Type] Gesture Demo")
        self.clock = pygame.time.Clock()
        
        # Camera and tracker
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)
        self.tracker = [Type]Tracker()
        
        # Circle properties
        self.circle_x = WINDOW_WIDTH - 300
        self.circle_y = WINDOW_HEIGHT // 2
        self.circle_radius = 50
        self.circle_color = ACCENT_PRIMARY
        
        self.active_gestures = []
    
    def process_gestures(self, state):
        """Process tracking state and update circle properties."""
        self.active_gestures = []
        if not state.is_present:
            return
        
        # Add gesture detection and circle property updates here
    
    def draw_camera_feed(self, frame):
        """Draw camera feed with thin border."""
        camera_y = (WINDOW_HEIGHT - CAMERA_HEIGHT) // 2
        border_rect = pygame.Rect(10, camera_y - 1, CAMERA_WIDTH + 2, CAMERA_HEIGHT + 2)
        pygame.draw.rect(self.screen, BORDER_COLOR, border_rect, 1)
        
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_rgb = cv2.resize(frame_rgb, (CAMERA_WIDTH, CAMERA_HEIGHT))
        frame_surface = pygame.surfarray.make_surface(frame_rgb.swapaxes(0, 1))
        self.screen.blit(frame_surface, (11, camera_y))
    
    def draw_ui(self):
        """Draw minimal UI elements."""
        font_large = pygame.font.Font(None, 44)
        font_medium = pygame.font.Font(None, 30)
        font_small = pygame.font.Font(None, 24)
        
        # Title
        title = font_large.render("[Type] Gesture Demo", True, TEXT_PRIMARY)
        self.screen.blit(title, (CAMERA_WIDTH + 60, 40))
        
        # Instructions (keep minimal)
        instructions = [
            "Gesture 1 — Action",
            "Gesture 2 — Action",
        ]
        
        y = 120
        for item in instructions:
            text = font_small.render(item, True, TEXT_SECONDARY)
            self.screen.blit(text, (CAMERA_WIDTH + 60, y))
            y += 28
        
        # Active gestures
        if self.active_gestures:
            active_text = ", ".join(self.active_gestures)
            gesture_text = font_medium.render(active_text, True, ACCENT_PRIMARY)
            self.screen.blit(gesture_text, (CAMERA_WIDTH + 60, WINDOW_HEIGHT - 70))
        
        # Footer
        footer = font_small.render("ESC to exit", True, TEXT_SECONDARY)
        self.screen.blit(footer, (WINDOW_WIDTH - 140, WINDOW_HEIGHT - 40))
    
    def draw_circle(self):
        """Draw the controlled circle."""
        pygame.draw.circle(
            self.screen,
            self.circle_color,
            (int(self.circle_x), int(self.circle_y)),
            int(self.circle_radius)
        )
    
    def run(self):
        """Main loop."""
        running = True
        
        while running:
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
    demo = [Type]GestureDemo()
    demo.run()

if __name__ == "__main__":
    main()
```

### Key Requirements

1. **Always show camera feed with annotations** - Users need to see landmarks/tracking data
2. **Keep UI minimal** - No unnecessary elements, clean and professional
3. **Test ALL gestures** - Every gesture for that type should be testable
4. **Clear visual feedback** - Users should immediately see when gestures are detected
5. **Simple controls** - ESC to exit, no complex interactions needed

### Gesture Detection Tuning

If a user reports that a gesture is not being detected properly for them:

1. **Check the threshold values** - Different people have different facial features and expressions
2. **Adjust sensitivity** - Lower thresholds make detection more sensitive, higher thresholds make it less sensitive
3. **Test with the user** - Have them run the CV test demo and observe what values work
4. **Update the gesture file** - Modify the threshold parameter in the gesture detection function

**Example:** For smile detection, some people's mouths don't curve as much, so the threshold may need to be lowered from `0.02` to `0.01` to make it more sensitive.

**Common adjustments:**
- Blink detection: Adjust EAR threshold (typically 0.18-0.25)
- Smile detection: Adjust corner elevation threshold (typically 0.01-0.03)
- Mouth open: Adjust MAR threshold (typically 0.03-0.06)
- Hand gestures: Adjust distance thresholds for pinch, fist, etc.
