#!/usr/bin/env python3
"""
Math-O-Lantern: A gesture-controlled educational math game

Players use hand gestures to slice falling pumpkins that display answers
to math problems, creating an engaging way to practice addition and subtraction.
"""

import os
import sys
import pygame
import random
import cv2
from enum import Enum
from dataclasses import dataclass
from typing import Dict, Optional, List

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Import HandTracker from kiro_interaction_kit
from kiro_interaction_kit.controllers.hand_controller import HandTracker

# Constants
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
FPS = 60

# Game states
class GameState(Enum):
    START = "start"
    INSTRUCTIONS = "instructions"
    GAMEPLAY = "gameplay"
    GAME_OVER = "game_over"


@dataclass
class Question:
    """Represents a math question with operands, operator, and answer"""
    operand1: int
    operator: str  # '+' or '-'
    operand2: int
    answer: int
    
    def get_expression(self) -> str:
        """Returns formatted expression like '6 + 25 = ?'"""
        return f"{self.operand1} {self.operator} {self.operand2} = ?"


@dataclass
class Pumpkin:
    """Represents a falling pumpkin with a number"""
    x: float
    y: float
    number: int
    is_correct: bool
    velocity_y: float
    image: pygame.Surface
    rect: pygame.Rect
    
    def update(self, delta_time: float) -> None:
        """Updates pumpkin position based on velocity"""
        self.y += self.velocity_y * delta_time
        self.rect.y = int(self.y)
    
    def is_off_screen(self, screen_height: int) -> bool:
        """Checks if pumpkin has fallen below screen"""
        return self.y > screen_height


@dataclass
class Effect:
    """Represents a visual effect (pie slice or cursed pumpkin)"""
    x: float
    y: float
    image: pygame.Surface
    duration: float  # seconds
    elapsed: float
    
    def update(self, delta_time: float) -> bool:
        """Updates effect timer, returns True if still active"""
        self.elapsed += delta_time
        return self.elapsed < self.duration


class PumpkinManager:
    """Manages pumpkin spawning, updating, and collision detection"""
    
    def __init__(self, pumpkin_image: pygame.Surface):
        """Initialize the pumpkin manager"""
        self.pumpkins: List[Pumpkin] = []
        self.spawn_timer: float = 0.0
        self.spawn_interval: float = 1.2  # seconds between spawns (adjusted for better gameplay)
        self.pumpkin_image = pumpkin_image
    
    def spawn_pumpkin(self, correct_answer: int, screen_width: int) -> None:
        """Spawns a pumpkin with correct (60%) or incorrect (40%) answer"""
        # Determine if this pumpkin should have the correct answer (60% chance)
        is_correct = random.random() < 0.6
        
        # Assign the number
        if is_correct:
            number = correct_answer
        else:
            # Generate an incorrect answer within ±50 of correct answer
            offset = random.randint(-50, 50)
            if offset == 0:  # Avoid accidentally creating correct answer
                offset = random.choice([-1, 1])
            number = correct_answer + offset
            # Ensure number is positive
            if number < 0:
                number = correct_answer + abs(offset)
        
        # Random x position across screen width
        # Leave some margin on edges for pumpkin size
        pumpkin_width = self.pumpkin_image.get_width()
        x = random.randint(pumpkin_width // 2, screen_width - pumpkin_width // 2)
        
        # Start above screen
        y = -100.0
        
        # Random fall velocity (120-180 pixels/second) - adjusted for better difficulty
        velocity_y = random.uniform(120.0, 180.0)
        
        # Create rect for collision detection
        rect = self.pumpkin_image.get_rect()
        rect.x = int(x)
        rect.y = int(y)
        
        # Create and add pumpkin
        pumpkin = Pumpkin(
            x=x,
            y=y,
            number=number,
            is_correct=is_correct,
            velocity_y=velocity_y,
            image=self.pumpkin_image,
            rect=rect
        )
        
        self.pumpkins.append(pumpkin)
    
    def update(self, delta_time: float, screen_height: int) -> None:
        """Updates all pumpkins and removes off-screen ones"""
        # Update spawn timer
        self.spawn_timer += delta_time
        
        # Update all pumpkins
        for pumpkin in self.pumpkins:
            pumpkin.update(delta_time)
        
        # Remove off-screen pumpkins
        self.pumpkins = [p for p in self.pumpkins if not p.is_off_screen(screen_height)]
    
    def check_collision(self, cursor_x: float, cursor_y: float) -> Optional[Pumpkin]:
        """Returns pumpkin if cursor overlaps it, None otherwise"""
        cursor_rect = pygame.Rect(int(cursor_x) - 10, int(cursor_y) - 10, 20, 20)
        
        for pumpkin in self.pumpkins:
            if cursor_rect.colliderect(pumpkin.rect):
                return pumpkin
        
        return None
    
    def remove_pumpkin(self, pumpkin: Pumpkin) -> None:
        """Removes specified pumpkin from list"""
        if pumpkin in self.pumpkins:
            self.pumpkins.remove(pumpkin)
    
    def clear_all(self) -> None:
        """Removes all pumpkins"""
        self.pumpkins.clear()


class QuestionManager:
    """Manages the question bank and current game session questions"""
    
    def __init__(self):
        """Initialize the question manager"""
        self.question_bank: List[Question] = []
        self.current_questions: List[Question] = []
        self.current_index: int = 0
        self.question_timer: float = 15.0
        
        # Initialize the question bank with 50 problems
        self.initialize_question_bank()
    
    def initialize_question_bank(self) -> None:
        """Creates 50 addition and subtraction problems (25 each)"""
        self.question_bank = []
        
        # Generate 25 addition problems
        # Mix of small (1-20), medium (20-100), and large (100-999) numbers - max 3 digits
        addition_problems = []
        
        # Small addition problems (10 problems)
        for _ in range(10):
            a = random.randint(1, 20)
            b = random.randint(1, 20)
            addition_problems.append(Question(a, '+', b, a + b))
        
        # Medium addition problems (10 problems)
        for _ in range(10):
            a = random.randint(20, 100)
            b = random.randint(20, 100)
            addition_problems.append(Question(a, '+', b, a + b))
        
        # Large addition problems (5 problems) - max 3 digits (999)
        for _ in range(5):
            a = random.randint(100, 999)
            b = random.randint(100, 999)
            addition_problems.append(Question(a, '+', b, a + b))
        
        # Generate 25 subtraction problems
        # Mix of small, medium, and large numbers
        subtraction_problems = []
        
        # Small subtraction problems (10 problems)
        for _ in range(10):
            a = random.randint(1, 20)
            b = random.randint(1, a)  # Ensure positive result
            subtraction_problems.append(Question(a, '-', b, a - b))
        
        # Medium subtraction problems (10 problems)
        for _ in range(10):
            a = random.randint(20, 100)
            b = random.randint(1, a)  # Ensure positive result
            subtraction_problems.append(Question(a, '-', b, a - b))
        
        # Large subtraction problems (5 problems) - max 3 digits (999)
        for _ in range(5):
            a = random.randint(100, 999)
            b = random.randint(1, a)  # Ensure positive result
            subtraction_problems.append(Question(a, '-', b, a - b))
        
        # Combine all problems into the question bank
        self.question_bank = addition_problems + subtraction_problems
        
        # Shuffle to mix addition and subtraction
        random.shuffle(self.question_bank)
    
    def select_random_questions(self) -> None:
        """Randomly selects 10 unique questions from the question bank"""
        self.current_questions = random.sample(self.question_bank, 10)
        self.current_index = 0
        self.question_timer = 15.0
    
    def get_current_question(self) -> Optional[Question]:
        """Returns current question or None if all complete"""
        if self.current_index < len(self.current_questions):
            return self.current_questions[self.current_index]
        return None
    
    def advance_question(self) -> None:
        """Moves to next question and resets timer"""
        self.current_index += 1
        self.question_timer = 15.0
    
    def update_timer(self, delta_time: float) -> bool:
        """Updates timer, returns True if time expired"""
        self.question_timer -= delta_time
        if self.question_timer <= 0:
            self.question_timer = 0
            return True
        return False
    
    def is_complete(self) -> bool:
        """Returns True if all questions have been shown"""
        return self.current_index >= len(self.current_questions)


class MathOLanternGame:
    """Main game class for Math-O-Lantern"""
    
    def __init__(self):
        """Initialize the game"""
        pygame.init()
        
        # Pygame setup
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Math-O-Lantern")
        self.clock = pygame.time.Clock()
        
        # Game state
        self.state = GameState.START
        self.running = True
        
        # Score and lives
        self.score: int = 0
        self.lives: int = 3
        
        # Question manager
        self.question_manager = QuestionManager()
        
        # Assets
        self.assets: Dict[str, pygame.Surface] = {}
        self.sound_effects: Dict[str, pygame.mixer.Sound] = {}
        self.load_assets()
        
        # Pumpkin manager (initialized after assets are loaded)
        self.pumpkin_manager = PumpkinManager(self.assets["pumpkin"])
        
        # Hand tracking setup
        self.camera = cv2.VideoCapture(0)
        self.hand_tracker = HandTracker()
        
        # Cursor position (initialize to center of screen)
        self.cursor_x: float = WINDOW_WIDTH / 2
        self.cursor_y: float = WINDOW_HEIGHT / 2
        
        # Camera dimensions for coordinate mapping
        self.camera_width = 640
        self.camera_height = 480
        
        # Effects list for visual feedback
        self.effects: List[Effect] = []
        
        # Track previous pinch state for edge detection
        self.previous_pinch_state: bool = False
        
        # Countdown timer for INSTRUCTIONS state (5 seconds)
        self.countdown: int = 5
        self.countdown_timer: float = 0.0
    
    def load_assets(self) -> None:
        """Load all image assets from Assets folder"""
        assets_dir = os.path.join(os.path.dirname(__file__), "Assets")
        
        # Define all required assets
        asset_files = {
            "start_screen": "start-game-screen.png",
            "how_to_play": "how-to-play.png",
            "game_background": "game-background.png",
            "pumpkin": "pumpkin.png",
            "slice_effect": "slice-effect.png",
            "cursed_effect": "cursed-pumpkin-effect.png",
            "heart": "heart.png",
            "hand_cursor": "hand-cursor.png"
        }
        
        # Assets that need to be scaled to fit the game window
        background_assets = {"start_screen", "how_to_play", "game_background"}
        
        # Load each asset
        for asset_name, filename in asset_files.items():
            asset_path = os.path.join(assets_dir, filename)
            try:
                loaded_image = pygame.image.load(asset_path).convert_alpha()
                
                # Scale background images to fit the game window (1920x1080 -> 1280x720)
                if asset_name in background_assets:
                    loaded_image = pygame.transform.scale(loaded_image, (WINDOW_WIDTH, WINDOW_HEIGHT))
                # Scale pumpkins larger (120x120)
                elif asset_name == "pumpkin":
                    loaded_image = pygame.transform.scale(loaded_image, (120, 120))
                # Scale effects larger (180x180)
                elif asset_name in ["slice_effect", "cursed_effect"]:
                    loaded_image = pygame.transform.scale(loaded_image, (180, 180))
                # Scale hearts to be much smaller (30x30)
                elif asset_name == "heart":
                    loaded_image = pygame.transform.scale(loaded_image, (30, 30))
                # Scale hand cursor larger (75x75)
                elif asset_name == "hand_cursor":
                    loaded_image = pygame.transform.scale(loaded_image, (75, 75))
                
                self.assets[asset_name] = loaded_image
                print(f"Loaded asset: {filename}")
            except pygame.error as e:
                print(f"Error loading asset {filename}: {e}")
                sys.exit(1)
        
        # Load and start background music
        music_path = os.path.join(assets_dir, "Background-Music.mp3")
        try:
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.set_volume(0.5)  # Set volume to 50%
            pygame.mixer.music.play(-1)  # Loop indefinitely (-1 means loop forever)
            print("Loaded and started background music")
        except pygame.error as e:
            print(f"Warning: Could not load background music: {e}")
            # Continue without music - don't exit
        
        # Load sound effects
        whoosh_path = os.path.join(assets_dir, "whoosh-effect.mp3")
        try:
            whoosh_sound = pygame.mixer.Sound(whoosh_path)
            whoosh_sound.set_volume(1.0)  # Set to maximum volume (100%) to be audible over music
            self.sound_effects["whoosh"] = whoosh_sound
            print("Loaded whoosh sound effect")
        except pygame.error as e:
            print(f"Warning: Could not load whoosh sound effect: {e}")
            # Continue without sound effect - don't exit
    
    def handle_events(self) -> None:
        """Process pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_RETURN:
                    # Handle Enter key for state transitions
                    self.handle_enter_key()
    
    def handle_enter_key(self) -> None:
        """Handle Enter key press for state transitions"""
        if self.state == GameState.START:
            # Transition from START to INSTRUCTIONS
            self.state = GameState.INSTRUCTIONS
            self.countdown = 5
            self.countdown_timer = 0.0
        elif self.state == GameState.GAME_OVER:
            # Restart the game
            self.restart_game()
    
    def restart_game(self) -> None:
        """Reset game state and transition to INSTRUCTIONS"""
        # Reset score and lives
        self.score = 0
        self.lives = 3
        
        # Select new random questions
        self.question_manager.select_random_questions()
        
        # Clear all pumpkins
        self.pumpkin_manager.clear_all()
        
        # Clear all effects
        self.effects.clear()
        
        # Transition to INSTRUCTIONS state
        self.state = GameState.INSTRUCTIONS
        self.countdown = 5
        self.countdown_timer = 0.0
    
    def update(self, delta_time: float) -> None:
        """Update game logic based on current state"""
        # Update hand tracking and cursor position
        hand_state = self.update_hand_tracking()
        
        # Update effects
        self.update_effects(delta_time)
        
        # State-specific updates
        if self.state == GameState.INSTRUCTIONS:
            # Update countdown timer
            self.update_countdown(delta_time)
        elif self.state == GameState.GAMEPLAY:
            # Update gameplay logic
            self.update_gameplay(delta_time, hand_state)
    
    def update_countdown(self, delta_time: float) -> None:
        """Update countdown timer for INSTRUCTIONS state"""
        self.countdown_timer += delta_time
        
        # Check if a full second has passed
        if self.countdown_timer >= 1.0:
            self.countdown_timer -= 1.0
            self.countdown -= 1
            
            # Check if countdown reached 0
            if self.countdown <= 0:
                # Transition to GAMEPLAY state
                self.start_gameplay()
    
    def start_gameplay(self) -> None:
        """Start gameplay by selecting questions and transitioning to GAMEPLAY state"""
        # Select random questions if not already selected
        if not self.question_manager.current_questions:
            self.question_manager.select_random_questions()
        
        # Transition to GAMEPLAY state
        self.state = GameState.GAMEPLAY
    
    def update_gameplay(self, delta_time: float, hand_state) -> None:
        """Update gameplay logic"""
        # Get current question
        current_question = self.question_manager.get_current_question()
        
        if current_question is None:
            # All questions complete - transition to GAME_OVER
            self.state = GameState.GAME_OVER
            self.pumpkin_manager.clear_all()
            return
        
        # Check if lives reached 0
        if self.lives <= 0:
            # Game over - transition to GAME_OVER
            self.state = GameState.GAME_OVER
            self.pumpkin_manager.clear_all()
            return
        
        # Update question timer
        if self.question_manager.update_timer(delta_time):
            # Timer expired - advance to next question
            self.question_manager.advance_question()
            # Clear all pumpkins when advancing to next question
            self.pumpkin_manager.clear_all()
        
        # Update pumpkin spawning and movement
        self.pumpkin_manager.update(delta_time, WINDOW_HEIGHT)
        
        # Check if it's time to spawn a new pumpkin
        if self.pumpkin_manager.spawn_timer >= self.pumpkin_manager.spawn_interval:
            self.pumpkin_manager.spawn_timer = 0.0
            self.pumpkin_manager.spawn_pumpkin(current_question.answer, WINDOW_WIDTH)
        
        # Handle slice action during gameplay
        if hand_state:
            self.handle_slice_action(hand_state)
    
    def update_hand_tracking(self):
        """Update hand tracking and cursor position, returns hand_state"""
        # Read camera frame
        success, frame = self.camera.read()
        if not success:
            # If camera read fails, keep cursor at last position
            return None
        
        # Process frame with hand tracker
        annotated_frame, hand_state = self.hand_tracker.process_frame(frame)
        
        # Update cursor position if hand is detected
        if hand_state.is_present and hand_state.cursor_x is not None:
            # Map normalized coordinates (0-1) to screen coordinates
            # cursor_x and cursor_y are already normalized by HandTracker
            self.cursor_x = hand_state.cursor_x * WINDOW_WIDTH
            self.cursor_y = hand_state.cursor_y * WINDOW_HEIGHT
        
        # If hand is not detected, cursor position persists (no update needed)
        return hand_state
    
    def handle_slice_action(self, hand_state) -> None:
        """Handle slice action when pinch gesture is detected with collision"""
        # Detect pinch gesture (edge detection - transition from not pinching to pinching)
        current_pinch = hand_state.is_pinch if hand_state.is_present else False
        
        # Check if this is a new pinch (rising edge)
        if current_pinch and not self.previous_pinch_state:
            # Check for collision with any pumpkin
            collided_pumpkin = self.pumpkin_manager.check_collision(self.cursor_x, self.cursor_y)
            
            if collided_pumpkin:
                # Play whoosh sound effect
                if "whoosh" in self.sound_effects:
                    self.sound_effects["whoosh"].play()
                
                # Execute slice action
                if collided_pumpkin.is_correct:
                    # Correct pumpkin sliced - spawn pie slice effect
                    self.spawn_effect(
                        collided_pumpkin.x,
                        collided_pumpkin.y,
                        self.assets["slice_effect"]
                    )
                    # Increment score by 5 points
                    self.score += 5
                else:
                    # Incorrect pumpkin sliced - spawn cursed pumpkin effect
                    self.spawn_effect(
                        collided_pumpkin.x,
                        collided_pumpkin.y,
                        self.assets["cursed_effect"]
                    )
                    # Decrement lives by 1
                    self.lives -= 1
                
                # Remove the pumpkin
                self.pumpkin_manager.remove_pumpkin(collided_pumpkin)
        
        # Update previous pinch state
        self.previous_pinch_state = current_pinch
    
    def spawn_effect(self, x: float, y: float, effect_image: pygame.Surface) -> None:
        """Spawn a visual effect at the specified position"""
        effect = Effect(
            x=x,
            y=y,
            image=effect_image,
            duration=1.0,  # Display for 1 second
            elapsed=0.0
        )
        self.effects.append(effect)
    
    def update_effects(self, delta_time: float) -> None:
        """Update all effects and remove expired ones"""
        # Update each effect and keep only active ones
        self.effects = [effect for effect in self.effects if effect.update(delta_time)]
    
    def render(self) -> None:
        """Render all visual elements based on current state"""
        # Clear screen
        self.screen.fill((0, 0, 0))
        
        # Render based on current state
        if self.state == GameState.START:
            # Display start screen
            self.screen.blit(self.assets["start_screen"], (0, 0))
        elif self.state == GameState.INSTRUCTIONS:
            # Display how-to-play screen
            self.screen.blit(self.assets["how_to_play"], (0, 0))
            
            # Render countdown
            self.render_countdown()
        elif self.state == GameState.GAMEPLAY:
            # Display game background
            self.screen.blit(self.assets["game_background"], (0, 0))
            
            # Render current question
            self.render_question()
            
            # Render question timer
            self.render_question_timer()
            
            # Render pumpkins
            self.render_pumpkins()
            
            # Render effects
            self.render_effects()
            
            # Render cursor during gameplay
            self.render_cursor()
            
            # Render score and lives
            self.render_score()
            self.render_lives()
        elif self.state == GameState.GAME_OVER:
            # Display game background for game over
            self.screen.blit(self.assets["game_background"], (0, 0))
            
            # Render final score and lives
            self.render_score()
            self.render_lives()
            
            # Render game over text
            self.render_game_over()
        
        # Update display
        pygame.display.flip()
    
    def render_pumpkins(self) -> None:
        """Render all pumpkins with their numbers"""
        font = pygame.font.Font(None, 38)  # Adjusted to fit 3-digit numbers in circle
        
        for pumpkin in self.pumpkin_manager.pumpkins:
            # Draw pumpkin image
            pumpkin_rect = pumpkin.image.get_rect()
            pumpkin_rect.center = (int(pumpkin.x), int(pumpkin.y))
            self.screen.blit(pumpkin.image, pumpkin_rect)
            
            # Draw number in a circle
            # Create a white circle background for the number
            circle_radius = 36  # Large enough for 3-digit numbers
            circle_x = int(pumpkin.x)
            circle_y = int(pumpkin.y) + 35  # Position below pumpkin center (adjusted for larger size)
            
            # Draw white circle background
            pygame.draw.circle(
                self.screen,
                (255, 255, 255),
                (circle_x, circle_y),
                circle_radius
            )
            
            # Draw black outline
            pygame.draw.circle(
                self.screen,
                (0, 0, 0),
                (circle_x, circle_y),
                circle_radius,
                2
            )
            
            # Draw number text
            number_text = font.render(str(pumpkin.number), True, (0, 0, 0))
            number_rect = number_text.get_rect(center=(circle_x, circle_y))
            self.screen.blit(number_text, number_rect)
    
    def render_effects(self) -> None:
        """Render all active effects"""
        for effect in self.effects:
            # Center the effect image at the effect position
            effect_rect = effect.image.get_rect()
            effect_rect.center = (int(effect.x), int(effect.y))
            self.screen.blit(effect.image, effect_rect)
    
    def render_cursor(self) -> None:
        """Render the cursor using hand cursor image"""
        hand_cursor = self.assets["hand_cursor"]
        
        # Center the hand cursor image at the cursor position
        cursor_rect = hand_cursor.get_rect()
        cursor_rect.center = (int(self.cursor_x), int(self.cursor_y))
        
        self.screen.blit(hand_cursor, cursor_rect)
    
    def render_score(self) -> None:
        """Render the score in the top left corner"""
        font = pygame.font.Font(None, 56)  # Larger font for better visibility
        score_text = font.render(f"Score: {self.score}", True, (255, 215, 0))  # Gold color
        
        # Add a black outline for better visibility
        score_outline = font.render(f"Score: {self.score}", True, (0, 0, 0))
        
        # Position in top left corner with some padding
        x = 25
        y = 25
        
        # Draw outline (slightly offset in all directions)
        for dx, dy in [(-2, -2), (-2, 2), (2, -2), (2, 2)]:
            self.screen.blit(score_outline, (x + dx, y + dy))
        
        # Draw main text
        self.screen.blit(score_text, (x, y))
    
    def render_lives(self) -> None:
        """Render heart icons for remaining lives"""
        heart_image = self.assets["heart"]
        
        # Position hearts below score in top left corner
        x_start = 25
        y = 90  # Below the score text
        
        # Space between hearts
        heart_spacing = 10
        heart_width = heart_image.get_width()
        
        # Draw hearts from left to right
        for i in range(self.lives):
            x = x_start + i * (heart_width + heart_spacing)
            self.screen.blit(heart_image, (x, y))
    
    def render_countdown(self) -> None:
        """Render countdown timer during INSTRUCTIONS state"""
        font = pygame.font.Font(None, 100)
        countdown_text = font.render(str(self.countdown), True, (255, 255, 255))
        
        # Add a black outline for better visibility
        countdown_outline = font.render(str(self.countdown), True, (0, 0, 0))
        
        # Position in top left corner
        text_rect = countdown_text.get_rect()
        text_rect.topleft = (40, 40)
        
        # Draw outline (slightly offset in all directions)
        for dx, dy in [(-3, -3), (-3, 3), (3, -3), (3, 3)]:
            outline_rect = countdown_outline.get_rect()
            outline_rect.topleft = (40 + dx, 40 + dy)
            self.screen.blit(countdown_outline, outline_rect)
        
        # Draw main text
        self.screen.blit(countdown_text, text_rect)
    
    def render_question(self) -> None:
        """Render current question at top of screen"""
        current_question = self.question_manager.get_current_question()
        if current_question:
            font = pygame.font.Font(None, 72)  # Larger font for better readability
            question_text = font.render(current_question.get_expression(), True, (255, 255, 255))
            
            # Add a black outline for better visibility
            question_outline = font.render(current_question.get_expression(), True, (0, 0, 0))
            
            # Center at top of screen
            text_rect = question_text.get_rect(center=(WINDOW_WIDTH // 2, 70))
            
            # Draw outline (thicker)
            for dx, dy in [(-3, -3), (-3, 3), (3, -3), (3, 3)]:
                outline_rect = question_outline.get_rect(center=(WINDOW_WIDTH // 2 + dx, 70 + dy))
                self.screen.blit(question_outline, outline_rect)
            
            # Draw main text
            self.screen.blit(question_text, text_rect)
    
    def render_question_timer(self) -> None:
        """Render question timer during gameplay"""
        font = pygame.font.Font(None, 52)  # Larger font
        timer_seconds = int(self.question_manager.question_timer)
        
        # Change color to red when time is running out (5 seconds or less)
        if timer_seconds <= 5:
            timer_color = (255, 69, 58)  # Red warning color
        else:
            timer_color = (255, 255, 255)  # White
        
        timer_text = font.render(f"Time: {timer_seconds}s", True, timer_color)
        
        # Add a black outline for better visibility
        timer_outline = font.render(f"Time: {timer_seconds}s", True, (0, 0, 0))
        
        # Position below the question
        text_rect = timer_text.get_rect(center=(WINDOW_WIDTH // 2, 140))
        
        # Draw outline
        for dx, dy in [(-2, -2), (-2, 2), (2, -2), (2, 2)]:
            outline_rect = timer_outline.get_rect(center=(WINDOW_WIDTH // 2 + dx, 140 + dy))
            self.screen.blit(timer_outline, outline_rect)
        
        # Draw main text
        self.screen.blit(timer_text, text_rect)
    
    def render_game_over(self) -> None:
        """Render game over text and restart prompt"""
        # Large "GAME OVER" text
        font_large = pygame.font.Font(None, 96)
        game_over_text = font_large.render("GAME OVER", True, (255, 255, 255))
        game_over_outline = font_large.render("GAME OVER", True, (0, 0, 0))
        
        # Center on screen
        text_rect = game_over_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 50))
        
        # Draw outline
        for dx, dy in [(-3, -3), (-3, 3), (3, -3), (3, 3)]:
            outline_rect = game_over_outline.get_rect(center=(WINDOW_WIDTH // 2 + dx, WINDOW_HEIGHT // 2 - 50 + dy))
            self.screen.blit(game_over_outline, outline_rect)
        
        # Draw main text
        self.screen.blit(game_over_text, text_rect)
        
        # Restart prompt
        font_small = pygame.font.Font(None, 48)
        restart_text = font_small.render("Hit enter to restart game", True, (255, 255, 255))
        restart_outline = font_small.render("Hit enter to restart game", True, (0, 0, 0))
        
        restart_rect = restart_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 50))
        
        # Draw outline
        for dx, dy in [(-2, -2), (-2, 2), (2, -2), (2, 2)]:
            outline_rect = restart_outline.get_rect(center=(WINDOW_WIDTH // 2 + dx, WINDOW_HEIGHT // 2 + 50 + dy))
            self.screen.blit(restart_outline, outline_rect)
        
        # Draw main text
        self.screen.blit(restart_text, restart_rect)
    
    def run(self) -> None:
        """Main game loop"""
        print("Starting Math-O-Lantern...")
        
        while self.running:
            # Calculate delta time
            delta_time = self.clock.tick(FPS) / 1000.0  # Convert to seconds
            
            # Process events
            self.handle_events()
            
            # Update game state
            self.update(delta_time)
            
            # Render
            self.render()
        
        # Cleanup
        pygame.mixer.music.stop()  # Stop background music
        self.camera.release()
        self.hand_tracker.close()
        pygame.quit()
        print("Game ended.")


def main():
    """Entry point for the game"""
    game = MathOLanternGame()
    game.run()


if __name__ == "__main__":
    main()
