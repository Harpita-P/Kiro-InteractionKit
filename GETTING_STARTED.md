# Getting Started with Kiro Motion Kit

This guide will help you set up Kiro Motion Kit and build your first gesture-controlled application.

## What Can You Build?

Kiro Motion Kit is perfect for creating:

- 🎮 **Games** - Fruit Ninja clones, rhythm games, fighting games, puzzle games
- 🎨 **Interactive Art** - Gesture-driven installations, digital paintings, music visualizers
- ♿ **Accessibility Tools** - Hands-free computer control, assistive interfaces
- 📊 **Presentations** - Gesture-controlled slides, interactive demos
- 📚 **Educational Apps** - Interactive learning tools, sign language tutors
- 🎵 **Music Controllers** - Air instruments, DJ controllers, sound synthesizers

## Prerequisites

- Python 3.x installed
- Webcam connected
- Basic Python knowledge

## Installation

### Step 1: Clone and Open in Kiro IDE

```bash
git clone <your-repo-url>
cd Kiro-Motion-Kit
# Open in Kiro IDE
```

### Step 2: Configure Context7 MCP (Required)

Kiro uses Context7 MCP to provide real-time MediaPipe and pygame documentation.

1. Open **Kiro Settings** → **MCP**
2. Add your **Context7 API key**
3. This enables Kiro to help you with:
   - MediaPipe landmark/pose detection
   - Creating custom gestures
   - Pygame best practices
   - Real-time documentation

### Step 3: Install Dependencies

**Option A: Automated Setup (Recommended)**

**macOS/Linux:**
```bash
./setup.sh
```

**Windows:**
```bash
setup.bat
```

**Option B: Manual Setup**

```bash
pip install -r requirements.txt
```

### Step 4: Understand the Template

**Hooks** (`.kiro/hooks/`) - Automation for integrating new gestures into controllers

**Steering Docs** (`.kiro/steering/`) - Guidelines for:
- Architecture patterns
- Gesture best practices
- Testing approach

## Recommended: Build with Specs

The best way to build gesture-controlled apps with Kiro:

### 1. Create a New Spec
In Kiro IDE, create a new spec for your app (e.g., "gesture-fruit-slicer")

### 2. Define Requirements
Describe what gestures and features you need

### 3. Design Architecture
Kiro helps you design the app structure with proper gesture integration

### 4. Generate Tasks
Get a step-by-step implementation plan

### 5. Build with Kiro
Implement each task with Kiro's assistance, leveraging Context7 for MediaPipe/pygame help

This spec-driven approach ensures:
- ✅ Clean separation of CV and game logic
- ✅ Proper gesture integration
- ✅ Well-structured code
- ✅ Comprehensive testing

## Understanding the Architecture

Kiro Motion Kit follows a simple pattern:

```
Camera → Tracker → Gesture State → Your App Logic
```

### Key Components

1. **Controllers** (`kiro_motion_kit/controllers/`)
   - `HandTracker` - Detects hand gestures
   - `HeadTracker` - Detects head movements
   - `FaceTracker` - Detects facial expressions

2. **Gesture State** - Simple dataclass with boolean flags
   - `state.is_pinch` - True when pinching
   - `state.is_closed` - True when fist is closed
   - `state.cursor_x/y` - Hand position (0-1)

3. **Your Game** - Reads state and updates game logic

## Your First App: Pinch Counter

Let's build a simple application where pinching increments a score. This demonstrates the core concepts you'll use in any gesture-controlled app.

### Step 1: Create App Folder

```bash
mkdir -p my_apps/pinch-counter
cd my_apps/pinch-counter
```

### Step 2: Create main.py

This simple app demonstrates the fundamental pattern used in all Kiro Motion Kit applications:

```python
import os, sys, cv2, pygame

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)

from kiro_motion_kit.controllers.hand_controller import HandTracker

def main():
    # Initialize Pygame
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 72)
    
    # Initialize CV
    cap = cv2.VideoCapture(0)
    tracker = HandTracker()
    
    # Game state
    score = 0
    prev_pinch = False  # For edge detection
    
    running = True
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        # Process gestures
        success, frame = cap.read()
        if success:
            _, state = tracker.process_frame(frame)
            
            # Edge detection: only increment when pinch starts
            if state.is_pinch and not prev_pinch:
                score += 1
            
            prev_pinch = state.is_pinch
        
        # Render
        screen.fill((30, 30, 30))
        text = font.render(f"Score: {score}", True, (255, 255, 255))
        screen.blit(text, (250, 250))
        
        instruction = pygame.font.Font(None, 36).render("Pinch to score!", True, (200, 200, 200))
        screen.blit(instruction, (280, 350))
        
        pygame.display.flip()
        clock.tick(30)
    
    # Cleanup
    cap.release()
    tracker.close()
    pygame.quit()

if __name__ == "__main__":
    main()
```

### Step 3: Run Your App

```bash
python my_apps/pinch-counter/main.py
```

**Congratulations!** You've built your first gesture-controlled application. This same pattern can be used to build games, interactive art, accessibility tools, and more.

## Key Concepts

### 1. Edge Detection

To detect when a gesture **starts** (not just when it's active):

```python
prev_pinch = False

# In game loop
if state.is_pinch and not prev_pinch:
    # Pinch just started - fire once!
    shoot_bullet()

prev_pinch = state.is_pinch
```

### 2. Continuous Actions

For actions that happen while gesture is held:

```python
if state.is_closed:
    # Happens every frame while fist is closed
    charge_power += 1
```

### 3. Cursor Position

Use hand position for movement:

```python
if state.is_present and state.cursor_x:
    player_x = int(state.cursor_x * SCREEN_WIDTH)
    player_y = int(state.cursor_y * SCREEN_HEIGHT)
```

### 4. Multiple Gestures

Track multiple gestures independently:

```python
prev_pinch = False
prev_fist = False

# In loop
if state.is_pinch and not prev_pinch:
    shoot()

if state.is_closed and not prev_fist:
    jump()

prev_pinch = state.is_pinch
prev_fist = state.is_closed
```

## Testing Gestures

Before building your game, test that gestures work on your system:

```bash
# Test hand gestures
python tests/CV-Test-Hands.py

# Test head gestures
python tests/CV-Test-Head.py

# Test face gestures
python tests/CV-Test-Face.py
```

These interactive demos show all available gestures and let you verify detection works properly.

## Available Gestures Reference

### Hand Gestures

| Gesture | Attribute | Description |
|---------|-----------|-------------|
| Fist | `state.is_closed` | Hand closed into fist |
| Pinch | `state.is_pinch` | Thumb and index touching |
| Peace | `state.is_peace` | Index and middle extended |
| Thumbs Up | `state.is_thumbs_up` | Thumb extended up |
| Thumbs Down | `state.is_thumbs_down` | Thumb extended down |
| Rock Sign | `state.is_rock_sign` | Index and pinky extended |
| Open Hand | `state.is_open_hand` | All fingers extended |
| Pointing | `state.is_pointing` | Index finger extended |
| OK Sign | `state.is_ok_sign` | Thumb and index circle |
| Position | `state.cursor_x/y` | Hand position (0-1) |

### Head Gestures

```python
from kiro_motion_kit.gestures.head_gestures import is_nod_up, is_nod_down, is_turn_left, is_turn_right

if is_nod_up(state.x_axis):
    # Head tilted up
```

### Face Gestures

| Gesture | Attribute | Description |
|---------|-----------|-------------|
| Blink | `state.is_blink` | Eyes closed |
| Smile | `state.is_smiling` | Smiling |
| Mouth Open | `state.is_mouth_open` | Mouth open |

## Application Ideas to Get You Started

### Beginner Projects
- **Gesture Counter** - Count different gestures (pinch, fist, peace)
- **Color Picker** - Change colors with different gestures
- **Simple Clicker** - Pinch to increment score
- **Hand Tracker** - Visualize hand position and gestures

### Intermediate Projects
- **Fruit Slicer** - Slice falling objects with gestures
- **Air Piano** - Play notes with different hand positions
- **Gesture Painter** - Draw with hand movements
- **Presentation Controller** - Navigate slides with gestures

### Advanced Projects
- **Rhythm Game** - Hit notes with timed gestures
- **Sign Language Tutor** - Learn and practice sign language
- **Fitness Tracker** - Count exercises with pose detection
- **Interactive Installation** - Create gesture-driven art

## Next Steps

1. **Read the Development Guide**: `.kiro/steering/game-development.md`
2. **Study the Template**: See the architecture patterns
3. **Build Your App**: Start with simple mechanics, add complexity gradually
4. **Share Your Creation**: Apps go in `my_apps/<your-app>/`

## Common Issues

### Camera Not Working
- Check camera permissions
- Try different camera index: `cv2.VideoCapture(1)` instead of `0`
- Ensure no other app is using the camera

### Gestures Not Detected
- Ensure good lighting
- Keep hand clearly visible to camera
- Adjust thresholds in tracker initialization if needed

### Import Errors
- Make sure you're running from project root
- Check that `PROJECT_ROOT` path is correct in your game

## Getting Help

- Check `.kiro/steering/game-development.md` for detailed guidelines
- Review CV test files in `tests/` for working examples
- Ensure all dependencies are installed: `pip install -r requirements.txt`

Happy coding! 🎮
