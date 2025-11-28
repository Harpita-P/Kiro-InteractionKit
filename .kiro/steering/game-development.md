---
inclusion: manual
---

# Game Development Guide for Kiro Motion Kit

This document defines the standard structure and conventions for creating gesture-controlled games using Kiro Motion Kit.

## Game Directory Structure

All games must follow this structure:

```
games/
└── <game-name>/
    ├── run.py                    # Entry point script
    ├── game.py                   # Main game class
    ├── README.md                 # Game documentation
    ├── entities/                 # Game objects
    │   ├── __init__.py
    │   ├── player.py
    │   ├── enemy.py
    │   └── ...
    ├── systems/                  # Game behavior engines
    │   ├── __init__.py
    │   ├── movement_system.py
    │   ├── collision_system.py
    │   └── ...
    └── mappings/                 # Gesture mappings
        ├── __init__.py
        └── <game-name>_mapping.py
```

## Required Components in Every Game

### 1. Game Loop (game.py)

Every game must have a `Game` class with:

**Required Methods:**
- `__init__()` - Initialize systems, entities, and event subscriptions
- `update(dt)` - Update game state (dt = delta time in seconds)
- `render(surface)` or `draw(frame)` - Render game to Pygame surface or OpenCV frame
- `cleanup()` or `close()` - Release resources

**Required Initialization:**
- Create all game systems
- Initialize entities
- Subscribe to gesture events via EventBus
- Set up game state variables

**Example Structure:**
```python
class Game:
    def __init__(self):
        self.bus = get_event_bus()
        self.entities = []
        self.systems = []
        self._setup_systems()
        self._setup_entities()
        self._subscribe_events()
    
    def _setup_systems(self):
        # Initialize systems
        pass
    
    def _setup_entities(self):
        # Initialize entities
        pass
    
    def _subscribe_events(self):
        # Subscribe to game.* events
        pass
    
    def update(self, dt):
        # Update all systems and entities
        pass
    
    def render(self, surface):
        # Draw all entities
        pass
    
    def cleanup(self):
        # Release resources
        pass
```

### 2. Entities

Entities are the objects in the game world.

**Examples:**
- Player
- Bird
- Fruit
- Enemy
- Obstacle
- UI elements (Score, Health Bar, Menu)

**Entity Conventions:**
- Place in `/games/<game>/entities/`
- Use clear, descriptive names: `bird.py`, `fruit.py`, `player.py`
- Each entity file should contain one primary class

**Required Entity Interface:**
```python
class Entity:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.velocity_x = 0
        self.velocity_y = 0
        self.active = True
    
    def update(self, dt):
        """Update entity state based on delta time."""
        pass
    
    def draw(self, surface):
        """Render entity to Pygame surface."""
        pass
```

**Entity Responsibilities:**
- Maintain own state (position, velocity, health, etc.)
- Update own state in `update(dt)`
- Render self in `draw(surface)`
- Provide collision bounds if needed
- NO game logic (that belongs in systems)

### 3. Systems

Systems are the behavior engines that operate on entities.

**Examples:**
- `MovementSystem` - Updates entity positions based on velocity
- `CollisionSystem` - Detects and resolves collisions
- `SpawnSystem` - Creates new entities over time
- `ScoreSystem` - Tracks and updates score
- `SliceSystem` - Handles slicing mechanics (e.g., Fruit Ninja)
- `JumpSystem` - Handles jumping mechanics (e.g., Flappy Bird)
- `AccessibilitySystem` - Provides visual/audio feedback for gestures

**System Conventions:**
- Place in `/games/<game>/systems/`
- Name with `System` suffix: `movement_system.py`
- Subscribe to gesture events through EventBus
- Never contain drawing logic
- Focus on pure game behavior

**Required System Interface:**
```python
class System:
    def __init__(self, game):
        self.game = game
        self.bus = get_event_bus()
        self._subscribe_events()
    
    def _subscribe_events(self):
        """Subscribe to relevant gesture events."""
        pass
    
    def update(self, dt):
        """Update system logic."""
        pass
```

**System Responsibilities:**
- Subscribe to `game.*` events (NOT `gesture.*` events directly)
- Operate on entities to implement game mechanics
- Maintain system-specific state
- NO rendering (entities handle their own rendering)

**System Design Principles:**
- Single Responsibility: Each system does one thing well
- Event-Driven: React to events, don't poll
- Stateless when possible: Operate on entity state
- Composable: Systems should work independently

### 4. Gesture → Action Mappings

Each game must have its own mapping file.

**Location:** `/games/<game>/mappings/<game-name>_mapping.py`

**Purpose:**
- Map low-level `gesture.*` events to high-level `game.*` actions
- Decouple gesture detection from game logic
- Allow customization without modifying core code

**Example:**
```python
from kiro_motion_kit import ActionMapper

_mapper = ActionMapper()

# Map gestures to game actions
_mapper.map_action(
    action="game.player.jump",
    gesture_event="gesture.closed.start",
)

_mapper.map_action(
    action="game.player.slice",
    gesture_event="gesture.peace.start",
)

_mapper.map_action(
    action="game.pause",
    gesture_event="gesture.thumbs_up.start",
)
```

**Mapping Conventions:**
- Use descriptive action names: `game.player.jump`, `game.enemy.spawn`
- Group related actions: `game.player.*`, `game.ui.*`
- Document non-obvious mappings in comments
- Import mapping in `run.py` to activate

### 5. Entry Script (run.py)

Every game must have a `run.py` entry point.

**Location:** `/games/<game>/run.py`

**Responsibilities:**
- Initialize Pygame window or OpenCV display
- Create game instance
- Initialize hand/face/head trackers
- Import gesture mappings
- Run main game loop
- Handle cleanup

**Required Structure:**
```python
import sys
import os
import pygame
import cv2

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from kiro_motion_kit import (
    HandInputManager,
    dispatch_gesture_events,
    get_event_bus,
)
from game import Game
from mappings import <game_name>_mapping  # Import to activate mappings

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
FPS = 60

def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("<Game Name>")
    clock = pygame.time.Clock()
    
    # Initialize camera and input
    cap = cv2.VideoCapture(0)
    hand_input = HandInputManager()
    
    # Initialize game
    game = Game()
    
    try:
        running = True
        while running:
            dt = clock.tick(FPS) / 1000.0  # Delta time in seconds
            
            # Handle Pygame events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            
            # ESC to quit
            keys = pygame.key.get_pressed()
            if keys[pygame.K_ESCAPE]:
                running = False
            
            # Process camera frame
            success, frame = cap.read()
            if success:
                actions, annotated_frame = hand_input.update_from_frame(frame)
                dispatch_gesture_events(actions)
            
            # Update and render game
            game.update(dt)
            game.render(screen)
            
            pygame.display.flip()
    
    finally:
        cap.release()
        hand_input.close()
        game.cleanup()
        pygame.quit()

if __name__ == "__main__":
    main()
```

### 6. Game README.md

Every game must have documentation.

**Location:** `/games/<game>/README.md`

**Required Sections:**
```markdown
# <Game Name>

## Description
Brief description of the game and its mechanics.

## How to Run
\`\`\`bash
python games/<game-name>/run.py
\`\`\`

## Gesture Controls
- **Closed Fist**: <action>
- **Pinch**: <action>
- **Peace Sign**: <action>
- **Thumbs Up**: <action>
- etc.

## Game Mechanics
Explain how the game works, scoring, win/lose conditions.

## Dependencies
List any additional dependencies beyond core Kiro Motion Kit.
```

## Rules for Creating New Games

When a user asks to create a new game:

1. **Test Gestures First (CRITICAL)**
   - Before building anything, create a simple gesture test script
   - Let the user physically test the gestures they proposed
   - Verify gestures are comfortable, detectable, and don't conflict
   - Create `/games/<game-name>/test_gestures.py` that:
     - Initializes the camera and appropriate tracker (hand/face/head)
     - Displays live camera feed with gesture detection overlay
     - Prints detected gestures to console
     - Shows which `gesture.*` events would fire
   - Ask user to confirm gestures work well before proceeding
   - Adjust gesture mappings based on user feedback

**Example test_gestures.py structure:**
```python
import cv2
from kiro_motion_kit import HandInputManager, dispatch_gesture_events, get_event_bus

def main():
    cap = cv2.VideoCapture(0)
    hand_input = HandInputManager()
    bus = get_event_bus()
    
    # Subscribe to all gesture events for testing
    def on_gesture(event_name):
        def handler(data):
            print(f"✓ {event_name} detected!")
        return handler
    
    bus.on("gesture.closed.start", on_gesture("CLOSED FIST"))
    bus.on("gesture.pinch.start", on_gesture("PINCH"))
    # ... add all gestures the game will use
    
    print("Testing gestures for <game-name>...")
    print("Press ESC to exit")
    
    while True:
        success, frame = cap.read()
        if not success:
            continue
        
        actions, annotated = hand_input.update_from_frame(frame)
        dispatch_gesture_events(actions)
        
        cv2.imshow("Gesture Test", annotated)
        if cv2.waitKey(1) & 0xFF == 27:  # ESC
            break
    
    cap.release()
    cv2.destroyAllWindows()
    hand_input.close()

if __name__ == "__main__":
    main()
```

2. **Create Directory Structure**
   - Create `/games/<game-name>/` directory
   - Create subdirectories: `entities/`, `systems/`, `mappings/`
   - Create `__init__.py` files in each subdirectory

3. **Start with Core Components**
   - Create `game.py` with basic Game class
   - Create `run.py` entry script
   - Create gesture mapping file

4. **Build Entities**
   - Identify all game objects
   - Create entity classes with `update()` and `draw()`
   - Keep entities simple and focused

5. **Implement Systems**
   - Identify game behaviors
   - Create system classes
   - Subscribe to `game.*` events
   - Implement `update()` logic

6. **Wire Up Mappings**
   - Map gestures to game actions
   - Import mapping in `run.py`
   - Test gesture responsiveness

7. **Test Game with Gestures**
   - Run the full game with camera
   - Verify all gesture mappings work as expected
   - Check for gesture fatigue or comfort issues
   - Iterate on mappings if needed

8. **Document**
   - Create README.md
   - Document gesture controls
   - Explain game mechanics

## Rules for Extending Existing Games

When a user asks to modify or extend an existing game:

1. **Never Modify Core Kiro Motion Kit**
   - All changes stay in `/games/<game-name>/`
   - Don't touch `kiro_motion_kit/` package

2. **Add New Systems, Don't Stuff Existing Ones**
   - Create new system files for new behaviors
   - Keep systems focused and single-purpose
   - Don't bloat existing systems

3. **Update Only the Specific Mapping File**
   - Modify `/games/<game>/mappings/<game>_mapping.py`
   - Don't create multiple mapping files per game
   - Keep mappings centralized

4. **Keep Game Logic Decoupled from Gesture Detection**
   - Systems subscribe to `game.*` events, not `gesture.*`
   - Mappings translate `gesture.*` to `game.*`
   - Never directly check gesture state in game logic

5. **Check if New System Needs Event Subscription**
   - If behavior is triggered by gesture, subscribe to event
   - If behavior is continuous, run in `update()`
   - Document event subscriptions clearly

## Architecture Flow

```
Camera Frame
    ↓
HandTracker / FaceTracker / HeadTracker
    ↓
HandInputManager / FaceInputManager
    ↓
dispatch_gesture_events()
    ↓
gesture.* events (e.g., gesture.closed.start)
    ↓
ActionMapper (game-specific mapping)
    ↓
game.* events (e.g., game.player.jump)
    ↓
Game Systems (subscribe to game.* events)
    ↓
Update Entities
    ↓
Render to Screen
```

## Best Practices

### Entity Design
- Keep entities dumb: they hold state, not logic
- Use composition over inheritance
- Provide clear interfaces for systems to interact

### System Design
- One system per behavior type
- Systems should be independent
- Use events for cross-system communication
- Avoid tight coupling between systems

### Event Naming
- Use hierarchical names: `game.player.jump`, `game.ui.pause`
- Be specific: `game.enemy.spawn` not `game.spawn`
- Use verbs for actions: `jump`, `slice`, `pause`

### Performance
- Limit entity count (pool and reuse)
- Avoid expensive operations in `update()`
- Use spatial partitioning for collision detection
- Profile before optimizing

### Accessibility
- Provide visual feedback for gestures
- Include audio cues for important events
- Support keyboard fallback for testing
- Consider gesture fatigue (don't require constant holding)

## Common Game Patterns

### Endless Runner
- **Entities**: Player, Obstacles, Background
- **Systems**: MovementSystem, CollisionSystem, SpawnSystem, ScoreSystem
- **Gestures**: Jump (closed fist), Duck (peace sign)

### Fruit Ninja Clone
- **Entities**: Fruit, Blade Trail, Score UI
- **Systems**: SliceSystem, SpawnSystem, ScoreSystem, PhysicsSystem
- **Gestures**: Slice (hand movement), Pause (thumbs up)

### Flappy Bird Clone
- **Entities**: Bird, Pipes, Ground, Score UI
- **Systems**: JumpSystem, CollisionSystem, ScrollSystem, ScoreSystem
- **Gestures**: Flap (closed fist or blink)

### Whack-a-Mole
- **Entities**: Mole, Hole, Hammer, Score UI
- **Systems**: SpawnSystem, HitDetectionSystem, ScoreSystem
- **Gestures**: Whack (pinch at cursor position)

## Testing Games

### Phase 1: Test Gestures BEFORE Building (REQUIRED)

**Always create a gesture test script first!**

Before writing any game code, create `test_gestures.py` to let the user:
- See live camera feed with gesture detection
- Physically perform the proposed gestures
- Verify gestures are comfortable and detectable
- Check for gesture conflicts or false positives
- Confirm gestures feel natural for the game mechanics

**Ask the user:** "I've created a gesture test script. Please run it and try out the gestures. Let me know if they feel comfortable and work well, or if we should adjust them."

Only proceed with game development after user confirms gestures work well.

### Phase 2: Test Game Logic Without Camera

1. **Test Without Camera First**
   - Use keyboard fallback for gestures
   - Verify game logic works independently
   - Debug game mechanics without gesture complexity

### Phase 3: Test Gesture Integration

2. **Test Gesture Mappings**
   - Verify each gesture triggers correct action
   - Check for gesture conflicts
   - Test edge cases (rapid gestures, holding)
   - Verify visual/audio feedback for gestures

### Phase 4: Test Performance and Polish

3. **Test Performance**
   - Monitor FPS with camera active
   - Check for memory leaks (long play sessions)
   - Profile bottlenecks

4. **Test Accessibility**
   - Verify visual feedback is clear
   - Check audio cues work
   - Test in different lighting conditions
   - Check for gesture fatigue (avoid constant holding)

## Example: Creating a Simple Game

User request: "Create a simple clicker game where I pinch to score points"

**Response:**
1. **First, test the gesture:**
   - Create `/games/clicker/test_gestures.py`
   - Test pinch gesture detection
   - Ask user: "Please run `python games/clicker/test_gestures.py` and try pinching. Does it detect reliably? Is it comfortable?"
   - Wait for user confirmation before proceeding

2. **After gesture confirmation, build the game:**
   - Create `/games/clicker/` structure
   - Create `game.py` with Game class, score counter
   - Create `entities/score_display.py` for UI
   - Create `systems/score_system.py` to handle scoring
   - Create `mappings/clicker_mapping.py` mapping pinch to `game.score.increment`
   - Create `run.py` entry script
   - Create README.md with controls

3. **Final testing:**
   - Run the full game
   - Verify pinch gesture increments score
   - Check for any issues or improvements

This ensures consistency, maintainability, and extensibility across all games built with Kiro Motion Kit.
