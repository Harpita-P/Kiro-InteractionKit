---
inclusion: manual
---

# Game Development Guide for Kiro InteractionKit

## Critical Rules

1. **Assets First**: Always ask users to provide ALL game assets BEFORE starting implementation. Never create placeholder assets.
2. **One Test File**: Create ONE comprehensive test file at the END of implementation as the final step before running the game.
3. **Check Gesture Attributes**: Always verify gesture attribute names in controller files before using them (e.g., `is_pinch` not `is_pinching`).
4. **Use Context7**: Reference pygame best practices via Context7 for proper game architecture and MediaPipe landmark/pose detection.
5. **Respect Template Structure**: Always follow the standard game template structure below.
6. **Separation of Concerns**: Keep CV gesture detection separate from game logic.

## Architecture Principles

### Separation of Concerns
- **CV Layer**: Controllers process frames and return gesture state
- **Game Layer**: Game logic reads state and updates game
- **Never mix**: Don't put game logic in CV code or CV processing in game logic

### Template Structure (ALWAYS FOLLOW)
```python
# 1. Imports
import os, sys, cv2, pygame
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)
from kiro_interaction_kit.controllers.hand_controller import HandTracker

# 2. Game Class or Functions (game logic only)
class Game:
    def __init__(self):
        # Initialize pygame, assets, game state
        pass
    
    def handle_gestures(self, state):
        # Read gesture state, update game
        pass
    
    def update(self, dt):
        # Update game logic
        pass
    
    def render(self):
        # Draw game
        pass

# 3. Main function (CV + game loop integration)
def main():
    # Initialize CV
    cap = cv2.VideoCapture(0)
    tracker = HandTracker()
    
    # Initialize game
    game = Game()
    
    # Game loop
    while running:
        # CV processing
        success, frame = cap.read()
        _, state = tracker.process_frame(frame)
        
        # Game update
        game.handle_gestures(state)
        game.update(dt)
        game.render()
    
    # Cleanup
    cap.release()
    tracker.close()
```

## Asset Requirements

Before starting ANY game implementation:
- Ask user for complete asset list with exact filenames
- Verify all assets are provided in the assets folder
- Document asset specifications (dimensions, formats)
- Never proceed without assets

## Core Principles

1. **All application code goes in `my_apps/<app-name>/`** - Never modify core library
2. **Direct controller usage** - No event systems or input managers needed
3. **Assets in app folder** - Each app manages its own assets

**Note**: The folder is called `my_apps/` (not `my_games/`) because Kiro InteractionKit can be used for any gesture-controlled application, not just games.

## Application Structure

```
my_apps/<app-name>/
├── main.py          # Entry point
├── README.md        # Documentation
└── assets/          # App assets (user-provided)
```

**Note**: While this guide focuses on game development, the same patterns apply to any gesture-controlled application (interactive art, accessibility tools, presentations, etc.).

## Gesture Usage

### Verify Attributes First
Always check controller files for correct attribute names:
```python
# Check kiro_interaction_kit/controllers/hand_controller.py
# HandTrackingState has: is_pinch, is_closed, is_peace, etc.
```

### Basic Pattern
```python
from kiro_interaction_kit.controllers.hand_controller import HandTracker

tracker = HandTracker()
cap = cv2.VideoCapture(0)

while running:
    success, frame = cap.read()
    _, state = tracker.process_frame(frame)
    
    if state.is_pinch:  # Correct: is_pinch
        slice_fruit()
    
    if state.is_present and state.cursor_x:
        x = int(state.cursor_x * WIDTH)
        y = int(state.cursor_y * HEIGHT)
```

### Edge Detection
```python
prev_pinch = False

# In loop
if state.is_pinch and not prev_pinch:
    on_pinch_start()  # Fires once
prev_pinch = state.is_pinch
```

## Simple Game Template

```python
import os, sys, cv2, pygame

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)

from kiro_interaction_kit.controllers.hand_controller import HandTracker

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()
    
    cap = cv2.VideoCapture(0)
    tracker = HandTracker()
    
    prev_pinch = False
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        success, frame = cap.read()
        if success:
            _, state = tracker.process_frame(frame)
            
            # Game logic here
            if state.is_pinch and not prev_pinch:
                # Action on pinch start
                pass
            prev_pinch = state.is_pinch
        
        # Render
        screen.fill((0, 0, 0))
        pygame.display.flip()
        clock.tick(60)
    
    cap.release()
    tracker.close()
    pygame.quit()

if __name__ == "__main__":
    main()
```

## Available Gestures

**Hand**: `is_closed`, `is_pinch`, `is_peace`, `is_thumbs_up`, `is_thumbs_down`, `is_rock_sign`, `is_open_hand`, `is_pointing`, `is_ok_sign`, `cursor_x`, `cursor_y`

**Head**: Use `HeadTracker` with `is_nod_up()`, `is_nod_down()`, `is_turn_left()`, `is_turn_right()` functions

**Face**: `is_blink`, `is_smiling`, `is_mouth_open`

## Creating New Gestures

When user requests a new gesture based on MediaPipe landmarks or pose detection:

1. **Use Context7** - Query Context7 for MediaPipe documentation and best practices
2. **Check Landmarks** - Understand which landmarks are needed for the gesture
3. **Create Gesture File** - Add to appropriate folder with proper naming:
   - Hand: `kiro_interaction_kit/gestures/hand_gestures/HA#_gesture_name.py`
   - Head: `kiro_interaction_kit/gestures/head_gestures/HE#_gesture_name.py`
   - Face: `kiro_interaction_kit/gestures/face_gestures/FA#_gesture_name.py`
4. **Update Controller** - Add gesture detection to controller's `process_frame()`
5. **Update State** - Add new attribute to tracking state dataclass
6. **Test Gesture** - Create/update CV test file to verify detection

## Testing

**ONE comprehensive test file as the FINAL step before running the game.**

Create `my_apps/<game-name>/test_game.py` that verifies:
- Assets load correctly
- Game initializes without errors
- Core game mechanics work
- Gesture detection integrates properly

This is the LAST task in implementation, right before running the game.

## Workflow

1. **Get Assets** - Ask user for ALL assets with exact filenames
2. **Verify Assets** - Confirm all files are in assets folder
3. **Follow Template** - Use the standard template structure above
4. **Implement** - Build game keeping CV and game logic separated
5. **Create Test** - ONE comprehensive test file as final implementation step
6. **Run Test** - Verify game works via test file
7. **Run Game** - Launch and play the game
8. **Document** - Create README with controls and run instructions
