# Kiro MotionMagic

MotionMagic is a Kiro code template that helps you build innovative gesture-controlled games & apps **without writing any computer vision code**. It transforms real-time MediaPipe hand, face, and head tracking into motion inputs you can use directly in your next Python app or Pygame project.

## What Can You Build?
Ever wanted to control a game by pinching the air? Tilt your head to move a character? Blink to trigger an effect? This kit lets you build those ideas instantly. It turns your gestures into clean inputs you can map to any interaction — from games and creative tools to accessibility apps and hands-free controls. Check out these ideas for some inspiration!

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
This kit includes pre-defined foundational logic for multiple hand, head, and face gestures, and uses a lightweight controller-based API that makes it easy to plug motion tracking directly into your game or app. You can easily add your own gestures by prompting Kiro.

## Available Gestures Reference

| **Hand Gestures** | **Head Gestures** | **Face Gestures** |
|-------------------|-------------------|-------------------|
| <table><tr><th>Emoji</th><th>Gesture</th><th>Attr</th></tr><tr><td>✊</td><td>Fist</td><td>`state.is_closed`</td></tr><tr><td>🤏</td><td>Pinch</td><td>`state.is_pinch`</td></tr><tr><td>✌️</td><td>Peace</td><td>`state.is_peace`</td></tr><tr><td>👍</td><td>Thumbs Up</td><td>`state.is_thumbs_up`</td></tr><tr><td>👎</td><td>Thumbs Down</td><td>`state.is_thumbs_down`</td></tr><tr><td>🤘</td><td>Rock Sign</td><td>`state.is_rock_sign`</td></tr><tr><td>🖐️</td><td>Open Hand</td><td>`state.is_open_hand`</td></tr><tr><td>👉</td><td>Pointing</td><td>`state.is_pointing`</td></tr><tr><td>👌</td><td>OK Sign</td><td>`state.is_ok_sign`</td></tr><tr><td>🎯</td><td>Position</td><td>`state.cursor_x/y`</td></tr></table> | <table><tr><th>Emoji</th><th>Gesture</th><th>Check</th></tr><tr><td>⬆️</td><td>Nod Up</td><td>`is_nod_up(state.x_axis)`</td></tr><tr><td>⬇️</td><td>Nod Down</td><td>`is_nod_down(state.x_axis)`</td></tr><tr><td>⬅️</td><td>Turn Left</td><td>`is_turn_left(state.y_axis)`</td></tr><tr><td>➡️</td><td>Turn Right</td><td>`is_turn_right(state.y_axis)`</td></tr><tr><td>↙️</td><td>Tilt Left</td><td>`state.z_axis < 0`</td></tr><tr><td>↘️</td><td>Tilt Right</td><td>`state.z_axis > 0`</td></tr></table> | <table><tr><th>Emoji</th><th>Gesture</th><th>Attr</th></tr><tr><td>😉</td><td>Blink</td><td>`state.is_blink`</td></tr><tr><td>😊</td><td>Smile</td><td>`state.is_smiling`</td></tr><tr><td>😮</td><td>Mouth Open</td><td>`state.is_mouth_open`</td></tr></table> |

## Quick Start

### 1. Clone and Open in Kiro IDE

```bash
git clone https://github.com/Harpita-P/Kiro-MotionMagic.git
cd Kiro-MotionMagic
# Open in Kiro IDE

# macOS / Linux
./setup.sh

# Windows
setup.bat
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

### 4. Test Your Camera and Existing Gestures

```bash
# Test hand gestures
python tests/CV-Test-Hands.py

# Test head gestures
python tests/CV-Test-Head.py

# Test face gestures
python tests/CV-Test-Face.py
```

### 5. Create Your First App with Specs

#### Building with Kiro IDE (Recommended)

This template is optimized for use with **Kiro IDE**:

#### Why Kiro IDE?
- **Spec-Driven Development** - Build apps systematically with requirements → design → tasks
- **Context7 Integration** - Real-time MediaPipe and pygame documentation
- **Auto-Integration Hooks** - Automatically integrate new gestures into controllers
- **Steering Docs** - Built-in guidelines for best practices

The recommended way to build with Kiro Motion Magic Template:

1. **Create a new spec** in Kiro IDE
2. **Define requirements** - What gestures and features you need
3. **Design architecture** - How your app will work
4. **Generate tasks** - Step-by-step implementation plan
5. **Build with Kiro** - Let Kiro help you implement each task

This spec-driven approach ensures clean architecture and proper gesture integration.

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

## Project Structure

```
Kiro-Motion-Kit/
├── kiro_motion_kit/          # Core library 
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

## Requirements

- Python 3.x
- Webcam or Camera
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
