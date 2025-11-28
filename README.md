# Kiro Motion Kit

A gesture recognition library for Python that enables touchless interaction with applications using computer vision. Build gesture-controlled games and applications with hand, head, and face tracking.

## What Can You Build?

Kiro Motion Kit empowers developers to create innovative gesture-controlled applications:

- 🎮 **Games** - Fruit Ninja clones, rhythm games, fighting games, puzzle games
- 🎨 **Interactive Art** - Gesture-driven installations, digital paintings, music visualizers
- ♿ **Accessibility Tools** - Hands-free computer control, assistive interfaces
- 📊 **Presentations** - Gesture-controlled slides, interactive demos
- 📚 **Educational Apps** - Interactive learning tools, sign language tutors
- 🎵 **Music Controllers** - Air instruments, DJ controllers, sound synthesizers
- 🏥 **Healthcare Apps** - Touchless medical interfaces, physical therapy tools
- 🎯 **Fitness Apps** - Exercise trackers, yoga pose detection, dance games

## Features

- **Hand Gestures**: Fist, pinch, peace sign, thumbs up/down, rock sign, open hand, pointing, OK sign
- **Head Gestures**: Nod up/down, turn left/right, tilt left/right
- **Face Gestures**: Blink, mouth open, smiling
- **Direct Controller API**: Simple, framework-agnostic gesture detection
- **Pygame Ready**: Perfect for building gesture-controlled games

## Quick Start

### 1. Clone and Open in Kiro IDE

```bash
git clone <your-repo-url>
cd Kiro-Motion-Kit
# Open in Kiro IDE
```

### 2. Configure Context7 MCP (Required)

Kiro uses Context7 MCP to provide up-to-date MediaPipe documentation and pygame best practices.

1. Open Kiro Settings → MCP
2. Add your Context7 API key
3. This enables Kiro to help you with:
   - MediaPipe landmark detection
   - Creating new gestures
   - Pygame best practices
   - Real-time documentation lookup

### 3. Understand the Template

**Hooks** (`.kiro/hooks/`) - Pre-configured automation for:
- Auto-integrating new hand gestures
- Auto-integrating new face gestures
- Auto-integrating new head gestures

**Steering Docs** (`.kiro/steering/`) - Development guidelines for:
- Game/app architecture patterns
- Gesture usage best practices
- Testing approach
- Project structure

### 4. Create Your First App with Specs

The recommended way to build with Kiro Motion Kit:

1. **Create a new spec** in Kiro IDE
2. **Define requirements** - What gestures and features you need
3. **Design architecture** - How your app will work
4. **Generate tasks** - Step-by-step implementation plan
5. **Build with Kiro** - Let Kiro help you implement each task

This spec-driven approach ensures clean architecture and proper gesture integration.

### 5. Test Your Camera and Gestures

```bash
# Test hand gestures
python tests/CV-Test-Hands.py

# Test head gestures
python tests/CV-Test-Head.py

# Test face gestures
python tests/CV-Test-Face.py
```

### 6. Build Your First App (Manual Approach)

Create a new game folder:

```bash
mkdir -p my_apps/my-game
cd my_apps/my-game
```

Create `main.py`:

```python
import os, sys, cv2, pygame

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)

from kiro_motion_kit.controllers.hand_controller import HandTracker

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()
    
    cap = cv2.VideoCapture(0)
    tracker = HandTracker()
    
    score = 0
    prev_pinch = False
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        success, frame = cap.read()
        if success:
            _, state = tracker.process_frame(frame)
            
            # Detect pinch to increment score
            if state.is_pinch and not prev_pinch:
                score += 1
            prev_pinch = state.is_pinch
        
        # Draw
        screen.fill((30, 30, 30))
        font = pygame.font.Font(None, 72)
        text = font.render(f"Score: {score}", True, (255, 255, 255))
        screen.blit(text, (250, 250))
        
        pygame.display.flip()
        clock.tick(30)
    
    cap.release()
    tracker.close()
    pygame.quit()

if __name__ == "__main__":
    main()
```

Run your game:

```bash
python my_apps/my-game/main.py
```

## Available Gestures

### Hand Gestures (HandTracker)

```python
from kiro_motion_kit.controllers.hand_controller import HandTracker

tracker = HandTracker()
_, state = tracker.process_frame(frame)

# Available attributes:
state.is_closed       # Fist
state.is_pinch        # Pinch (thumb + index)
state.is_peace        # Peace sign
state.is_thumbs_up    # Thumbs up
state.is_thumbs_down  # Thumbs down
state.is_rock_sign    # Rock sign (index + pinky)
state.is_open_hand    # Open hand
state.is_pointing     # Pointing
state.is_ok_sign      # OK sign
state.cursor_x        # Normalized x position (0-1)
state.cursor_y        # Normalized y position (0-1)
```

### Head Gestures (HeadTracker)

```python
from kiro_motion_kit.controllers.head_controller import HeadTracker
from kiro_motion_kit.gestures.head_gestures import is_nod_up, is_nod_down, is_turn_left, is_turn_right

tracker = HeadTracker()
_, state = tracker.process_frame(frame)

if is_nod_up(state.x_axis):
    print("Nodding up")
```

### Face Gestures (FaceTracker)

```python
from kiro_motion_kit.controllers.face_controller import FaceTracker

tracker = FaceTracker()
_, state = tracker.process_frame(frame)

# Available attributes:
state.is_blink        # Eyes closed
state.is_smiling      # Smiling
state.is_mouth_open   # Mouth open
```

## Example Applications

Here are some ideas to inspire your next project:

### Games
- **Fruit Slicer** - Slice falling fruits with pinch gestures
- **Rhythm Game** - Hit notes with timed hand movements
- **Fighting Game** - Punch and block with fist gestures
- **Puzzle Game** - Rotate pieces with head tilts

### Interactive Art
- **Gesture Painter** - Draw with hand movements, change colors with gestures
- **Music Visualizer** - Control visuals with hand position and gestures
- **Particle System** - Manipulate particles with hand movements
- **Light Controller** - Control smart lights with gestures

### Accessibility Tools
- **Hands-Free Mouse** - Control cursor with head movements
- **Gesture Keyboard** - Type with pinch gestures
- **Voice-Free Communication** - Use gestures to trigger pre-recorded messages
- **Assistive Browser** - Navigate web pages with gestures

### Educational Apps
- **Sign Language Tutor** - Learn and practice sign language
- **Math Game** - Answer questions with gesture-based input
- **Typing Tutor** - Practice typing with gesture keyboard
- **Music Lessons** - Learn instruments with air gestures

## Project Structure

```
Kiro-Motion-Kit/
├── kiro_motion_kit/          # Core library (don't modify)
│   ├── controllers/          # Hand, head, face trackers
│   ├── gestures/             # Gesture detection functions
│   └── utils/                # Helper utilities
├── my_apps/                  # Your applications go here
│   └── <app-name>/
│       ├── main.py           # App entry point
│       ├── assets/           # App assets
│       └── README.md         # App documentation
├── tests/                    # CV test demos
└── .kiro/                    # Kiro IDE configuration
```

## Building with Kiro IDE (Recommended)

This template is optimized for use with **Kiro IDE**:

### Why Kiro IDE?
- **Spec-Driven Development** - Build apps systematically with requirements → design → tasks
- **Context7 Integration** - Real-time MediaPipe and pygame documentation
- **Auto-Integration Hooks** - Automatically integrate new gestures into controllers
- **Steering Docs** - Built-in guidelines for best practices

### Getting Started with Kiro
1. Clone this repo and open in Kiro IDE
2. Configure Context7 MCP with your API key (Settings → MCP)
3. Create a new spec for your app
4. Let Kiro guide you through requirements, design, and implementation

### Manual Development
You can also build without Kiro IDE - just follow the patterns in `.kiro/steering/game-development.md`

## Development Guide

See `.kiro/steering/game-development.md` for detailed guidelines on:
- App architecture patterns
- Gesture usage best practices
- Asset management
- Testing approach
- Creating new gestures

## Requirements

- Python 3.x
- Webcam
- Dependencies in `requirements.txt`:
  - mediapipe (gesture detection)
  - opencv-python (camera processing)
  - pygame (game framework)
  - pyautogui (system automation)

## Examples

Check the `tests/` folder for interactive CV test demos that show all available gestures in action.

## Contributing

When adding new gestures:
1. Add gesture detection function to appropriate folder in `kiro_motion_kit/gestures/`
2. Update the controller to use the new gesture
3. Add the gesture to the tracking state dataclass
4. Create/update CV test file to demonstrate the gesture

## License

See LICENSE file for details.
