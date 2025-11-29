# Design Document: Math-O-Lantern

## Overview

Math-O-Lantern is a gesture-controlled educational game built using Pygame and the Kiro InteractionKit framework. The game presents players with timed math problems while pumpkins displaying potential answers fall across the screen. Players use hand tracking and pinch gestures to slice pumpkins with correct answers, earning points while avoiding incorrect answers that cost lives.

The architecture follows a game state machine pattern with distinct states for start screen, instructions, gameplay, and game over. The game leverages the existing HandTracker from the Kiro InteractionKit for gesture recognition and implements custom game logic for question management, pumpkin spawning, collision detection, and scoring.

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Math-O-Lantern Game                      │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Game State   │  │   Question   │  │   Pumpkin    │      │
│  │  Manager     │  │   Manager    │  │   Manager    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│         │                  │                  │              │
│         └──────────────────┴──────────────────┘              │
│                           │                                  │
│                  ┌────────▼────────┐                         │
│                  │  Game Renderer  │                         │
│                  └────────┬────────┘                         │
│                           │                                  │
└───────────────────────────┼──────────────────────────────────┘
                            │
                  ┌─────────▼─────────┐
                  │ Kiro InteractionKit│
                  │   (HandTracker)    │
                  └────────────────────┘
```

### Component Responsibilities

1. **Game State Manager**: Controls transitions between START, INSTRUCTIONS, GAMEPLAY, and GAME_OVER states
2. **Question Manager**: Maintains the question bank, selects random questions, and tracks current question
3. **Pumpkin Manager**: Spawns, updates, and removes pumpkins; handles collision detection
4. **Game Renderer**: Draws all visual elements including backgrounds, UI, pumpkins, and effects
5. **HandTracker** (from Kiro InteractionKit): Provides hand position and pinch gesture detection

## Components and Interfaces

### GameState Enum

```python
from enum import Enum

class GameState(Enum):
    START = "start"
    INSTRUCTIONS = "instructions"
    GAMEPLAY = "gameplay"
    GAME_OVER = "game_over"
```

### Question Class

```python
@dataclass
class Question:
    operand1: int
    operator: str  # '+' or '-'
    operand2: int
    answer: int
    
    def get_expression(self) -> str:
        """Returns formatted expression like '6 + 25 = ?'"""
        return f"{self.operand1} {self.operator} {self.operand2} = ?"
```

### Pumpkin Class

```python
@dataclass
class Pumpkin:
    x: float
    y: float
    number: int
    is_correct: bool
    velocity_y: float
    image: pygame.Surface
    rect: pygame.Rect
    
    def update(self, delta_time: float) -> None:
        """Updates pumpkin position based on velocity"""
        
    def is_off_screen(self, screen_height: int) -> bool:
        """Checks if pumpkin has fallen below screen"""
```

### Effect Class

```python
@dataclass
class Effect:
    x: float
    y: float
    image: pygame.Surface
    duration: float  # seconds
    elapsed: float
    
    def update(self, delta_time: float) -> bool:
        """Updates effect timer, returns True if still active"""
```

### QuestionManager Class

```python
class QuestionManager:
    def __init__(self):
        self.question_bank: List[Question] = []
        self.current_questions: List[Question] = []
        self.current_index: int = 0
        self.question_timer: float = 15.0
        
    def initialize_question_bank(self) -> None:
        """Creates 50 addition and subtraction problems"""
        
    def select_random_questions(self) -> None:
        """Randomly selects 10 unique questions from bank"""
        
    def get_current_question(self) -> Optional[Question]:
        """Returns current question or None if all complete"""
        
    def advance_question(self) -> None:
        """Moves to next question and resets timer"""
        
    def update_timer(self, delta_time: float) -> bool:
        """Updates timer, returns True if time expired"""
        
    def is_complete(self) -> bool:
        """Returns True if all questions have been shown"""
```

### PumpkinManager Class

```python
class PumpkinManager:
    def __init__(self, pumpkin_image: pygame.Surface):
        self.pumpkins: List[Pumpkin] = []
        self.spawn_timer: float = 0.0
        self.spawn_interval: float = 1.5  # seconds between spawns
        self.pumpkin_image = pumpkin_image
        
    def spawn_pumpkin(self, correct_answer: int, screen_width: int) -> None:
        """Spawns a pumpkin with correct (80%) or incorrect (20%) answer"""
        
    def update(self, delta_time: float, screen_height: int) -> None:
        """Updates all pumpkins and removes off-screen ones"""
        
    def check_collision(self, cursor_x: float, cursor_y: float) -> Optional[Pumpkin]:
        """Returns pumpkin if cursor overlaps it, None otherwise"""
        
    def remove_pumpkin(self, pumpkin: Pumpkin) -> None:
        """Removes specified pumpkin from list"""
        
    def clear_all(self) -> None:
        """Removes all pumpkins"""
```

### MathOLanternGame Class

```python
class MathOLanternGame:
    def __init__(self):
        # Pygame setup
        self.screen: pygame.Surface
        self.clock: pygame.time.Clock
        
        # Game state
        self.state: GameState = GameState.START
        self.score: int = 0
        self.lives: int = 3
        
        # Managers
        self.question_manager: QuestionManager
        self.pumpkin_manager: PumpkinManager
        
        # Hand tracking
        self.hand_tracker: HandTracker
        self.cursor_x: float = 0
        self.cursor_y: float = 0
        
        # Assets
        self.assets: Dict[str, pygame.Surface] = {}
        self.effects: List[Effect] = []
        
        # Countdown timer for instructions
        self.countdown: int = 10
        self.countdown_timer: float = 0.0
        
    def load_assets(self) -> None:
        """Loads all image assets from Assets folder"""
        
    def handle_events(self) -> bool:
        """Processes pygame events, returns False to quit"""
        
    def update(self, delta_time: float) -> None:
        """Updates game logic based on current state"""
        
    def render(self) -> None:
        """Renders all visual elements based on current state"""
        
    def run(self) -> None:
        """Main game loop"""
```

## Data Models

### Question Bank Structure

The question bank contains 50 pre-defined math problems:
- 25 addition problems (e.g., 6 + 25, 123 + 456)
- 25 subtraction problems (e.g., 14 - 9, 456 - 123)
- Numbers range from 1 to 4 digits
- Mix of positive and negative results for subtraction

### Game State Data

```python
{
    "state": GameState,
    "score": int,
    "lives": int,
    "current_question_index": int,
    "question_timer": float,
    "countdown": int,
    "pumpkins": List[Pumpkin],
    "effects": List[Effect]
}
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Question bank contains only valid operations
*For any* question in the question bank, the operator must be either '+' or '-'
**Validates: Requirements 3.2**

### Property 2: Question bank operands are within digit limits
*For any* question in the question bank, both operands must be between 1 and 9999 (up to 4 digits)
**Validates: Requirements 3.3**

### Property 3: Game session selects unique questions
*For any* game session, the 10 selected questions must all be unique (no duplicates)
**Validates: Requirements 3.4**

### Property 4: Questions are presented in selection order
*For any* game session, questions must be presented in the same order they were selected
**Validates: Requirements 3.5**

### Property 5: Question expression format is correct
*For any* question, the formatted expression must match the pattern "a [+|-] b = ?" where a and b are the operands
**Validates: Requirements 4.2**

### Property 6: Question timer advances to next question on expiration
*For any* active question, when the timer reaches 0 seconds, the system must advance to the next question
**Validates: Requirements 4.4**

### Property 7: Question timer initializes to 15 seconds
*For any* question when it becomes active, the timer must be set to 15 seconds
**Validates: Requirements 4.5**

### Property 8: Spawned pumpkins have assigned numbers
*For any* spawned pumpkin, it must have a number that is either the correct answer or an incorrect answer to the current question
**Validates: Requirements 5.2, 5.3**

### Property 9: Correct answer distribution is approximately 80%
*For any* large sample of spawned pumpkins (n > 100), approximately 80% (±5%) must have the correct answer
**Validates: Requirements 5.4**

### Property 10: Pumpkins move downward over time
*For any* pumpkin, its y-position must increase (move down) as time progresses
**Validates: Requirements 5.6**

### Property 11: Off-screen pumpkins are removed
*For any* pumpkin, when its y-position exceeds the screen height, it must be removed from the game
**Validates: Requirements 5.7**

### Property 12: Cursor position tracks hand position
*For any* frame where the HandTracker detects a hand, the cursor position must match the detected hand position
**Validates: Requirements 6.3**

### Property 13: Cursor position persists without hand detection
*For any* frame where the HandTracker does not detect a hand, the cursor position must remain unchanged from the previous frame
**Validates: Requirements 6.4**

### Property 14: Pinch gesture with collision triggers slice
*For any* pumpkin, when a pinch gesture is detected AND the cursor overlaps the pumpkin, a slice action must be executed
**Validates: Requirements 7.1**

### Property 15: Sliced pumpkins are removed
*For any* pumpkin that is sliced (correct or incorrect), it must be removed from the game
**Validates: Requirements 7.3, 7.6**

### Property 16: Incorrect slice decrements lives
*For any* incorrect pumpkin that is sliced, the player's life count must decrease by exactly 1
**Validates: Requirements 7.5**

### Property 17: Correct slice increments score
*For any* correct pumpkin that is sliced, the score must increase by exactly 5 points
**Validates: Requirements 9.3**

### Property 18: Displayed score matches internal score
*For any* game state during gameplay, the displayed score value must match the internal score variable
**Validates: Requirements 9.4**

### Property 19: Displayed hearts match life count
*For any* game state during gameplay, the number of displayed heart icons must equal the current life count
**Validates: Requirements 8.2**

### Property 20: Game ends after 10 questions
*For any* game session, when all 10 questions have been presented, the game state must transition to GAME_OVER
**Validates: Requirements 10.1**

### Property 21: Game ends when lives reach zero
*For any* game state, when the life count reaches 0, the game state must transition to GAME_OVER
**Validates: Requirements 10.2**

### Property 22: No pumpkins spawn in game over state
*For any* frame in GAME_OVER state, no new pumpkins must be spawned
**Validates: Requirements 10.3**

### Property 23: Restart resets game state
*For any* game over state, when Enter is pressed, the score must reset to 0, lives must reset to 3, new questions must be selected, and state must transition to INSTRUCTIONS
**Validates: Requirements 11.2, 11.3, 11.4, 11.5**

### Property 24: Countdown decrements each second
*For any* countdown value greater than 0, after 1 second has elapsed, the countdown must decrease by 1
**Validates: Requirements 2.3**

### Property 25: State remains until Enter is pressed
*For any* START state, the game state must not change until the Enter key is pressed
**Validates: Requirements 1.2**

## Error Handling

### Camera and Hand Tracking Errors

- **No camera available**: Display error message and exit gracefully
- **Hand tracking initialization fails**: Display error message and exit gracefully
- **Hand not detected**: Maintain cursor at last known position (no error state)

### Asset Loading Errors

- **Missing asset files**: Display specific error message indicating which asset is missing and exit
- **Invalid image format**: Display error message and exit
- **Asset path incorrect**: Verify all assets are in `my_apps/Math-O-Lantern/Assets/` directory

### Game Logic Errors

- **Question bank initialization fails**: Ensure question bank always has exactly 50 valid questions
- **Random selection fails**: Fallback to sequential selection if random fails
- **Timer becomes negative**: Clamp timer to 0 minimum

### Pygame Errors

- **Display initialization fails**: Display error message and exit
- **Font loading fails**: Use pygame default font as fallback
- **Event processing errors**: Log error and continue game loop

## Testing Strategy

### Unit Testing

The game will use Python's built-in `unittest` framework for unit tests. Unit tests will focus on:

1. **Question Management**:
   - Test question bank initialization creates exactly 50 questions
   - Test question formatting produces correct string format
   - Test random selection produces 10 unique questions
   - Test question advancement logic

2. **Pumpkin Management**:
   - Test pumpkin spawning with correct/incorrect answers
   - Test pumpkin movement and position updates
   - Test off-screen detection and removal
   - Test collision detection with cursor

3. **Game State Transitions**:
   - Test state transitions for each user input (Enter key)
   - Test countdown timer behavior
   - Test question timer behavior
   - Test game over conditions (all questions complete, lives = 0)

4. **Scoring and Lives**:
   - Test score increment on correct slice
   - Test life decrement on incorrect slice
   - Test initial values (score = 0, lives = 3)
   - Test restart resets values

### Property-Based Testing

The game will use **Hypothesis** (Python's property-based testing library) for property-based tests. Each property-based test will run a minimum of 100 iterations.

Property-based tests will verify:

1. **Question Bank Properties** (Properties 1, 2):
   - Generate random question banks and verify all operators are '+' or '-'
   - Verify all operands are within 1-9999 range

2. **Question Selection Properties** (Properties 3, 4):
   - Generate random selections and verify uniqueness
   - Verify presentation order matches selection order

3. **Pumpkin Behavior Properties** (Properties 8, 9, 10, 11):
   - Generate random pumpkin spawns and verify answer distribution
   - Verify downward movement over time
   - Verify removal when off-screen

4. **Cursor Tracking Properties** (Properties 12, 13):
   - Generate random hand positions and verify cursor synchronization
   - Verify cursor persistence when hand not detected

5. **Slice Action Properties** (Properties 14, 15, 16, 17):
   - Generate random slice scenarios and verify correct behavior
   - Verify pumpkin removal, life decrement, score increment

6. **Game State Properties** (Properties 20, 21, 22, 23):
   - Verify game over conditions trigger correctly
   - Verify restart resets all state correctly

Each property-based test must be tagged with a comment explicitly referencing the correctness property from this design document using the format: `# Feature: math-o-lantern-game, Property {number}: {property_text}`

### Integration Testing

Integration tests will verify:

1. **Hand Tracking Integration**: Verify HandTracker from Kiro InteractionKit correctly provides hand position and pinch detection
2. **Asset Loading**: Verify all 7 assets load correctly from the Assets folder
3. **Full Game Flow**: Verify complete game flow from start to game over to restart
4. **Pygame Integration**: Verify rendering, event handling, and game loop function correctly

### Manual Testing

Manual testing will focus on:

1. **Gesture Recognition**: Verify pinch gesture is reliably detected
2. **Visual Feedback**: Verify effects (pie slice, cursed pumpkin) display correctly
3. **Timing**: Verify 15-second question timer and 10-second countdown feel appropriate
4. **Difficulty**: Verify pumpkin spawn rate and fall speed create appropriate challenge
5. **User Experience**: Verify game is fun and educational

## Implementation Notes

### Pumpkin Spawning Strategy

- Spawn interval: 1.5 seconds (configurable)
- Random x-position across screen width
- Initial y-position: -100 (above screen)
- Fall velocity: 100-150 pixels/second (slight randomization for variety)
- Answer selection: 80% correct (use random.random() < 0.8)
- Incorrect answers: Generate random numbers within ±50 of correct answer

### Collision Detection

Use pygame.Rect for collision detection:
```python
cursor_rect = pygame.Rect(cursor_x - 10, cursor_y - 10, 20, 20)
pumpkin_rect = pumpkin.rect
if cursor_rect.colliderect(pumpkin_rect):
    # Collision detected
```

### Effect Animation

Effects display for 0.5 seconds then disappear:
- Create Effect object with duration = 0.5
- Update elapsed time each frame
- Remove when elapsed >= duration

### Hand Position Mapping

Map hand position from camera coordinates to screen coordinates:
```python
# Camera is typically 640x480, game screen is larger
screen_x = (hand_x / camera_width) * screen_width
screen_y = (hand_y / camera_height) * screen_height
```

### Question Bank Generation

Generate diverse questions:
- Small numbers: 1-20 (easier)
- Medium numbers: 20-100 (moderate)
- Large numbers: 100-9999 (harder)
- Mix of positive and negative results for subtraction
- Ensure no duplicate questions in bank

### Performance Considerations

- Limit maximum pumpkins on screen: 20
- Remove effects after animation completes
- Use pygame.sprite.Group for efficient collision detection (optional optimization)
- Blit images once, reuse surfaces

### File Structure

```
my_apps/Math-O-Lantern/
├── main.py                 # Main game file
├── Assets/
│   ├── start-game-screen.png
│   ├── how-to-play.png
│   ├── game-background.png
│   ├── pumpkin.png
│   ├── slice-effect.png
│   ├── cursed-pumpkin-effect.png
│   └── heart.png
└── README.md              # Game documentation
```

All game code will be in `main.py` to keep the implementation simple and self-contained.
