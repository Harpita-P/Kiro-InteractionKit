# Implementation Plan

- [x] 1. Set up project structure and load assets
  - Create `my_apps/Math-O-Lantern/main.py` file
  - Implement asset loading function to load all 7 images from Assets folder
  - Initialize Pygame window (1280x720 resolution)
  - Set up basic game loop structure with clock
  - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5, 12.6, 12.7_

- [x] 2. Implement Question data model and question bank
  - Create Question dataclass with operand1, operator, operand2, answer fields
  - Implement get_expression() method to format questions as "a + b = ?"
  - Create QuestionManager class with question bank initialization
  - Generate 50 math problems (25 addition, 25 subtraction) with numbers up to 4 digits
  - _Requirements: 3.1, 3.2, 3.3, 4.2_

- [ ]* 2.1 Write property test for question bank validation
  - **Property 1: Question bank contains only valid operations**
  - **Property 2: Question bank operands are within digit limits**
  - **Validates: Requirements 3.2, 3.3**

- [x] 3. Implement question selection and management
  - Implement select_random_questions() to choose 10 unique questions
  - Implement get_current_question() to return active question
  - Implement advance_question() to move to next question
  - Add question timer (15 seconds) with update logic
  - _Requirements: 3.4, 3.5, 4.5_

- [ ]* 3.1 Write property test for question selection
  - **Property 3: Game session selects unique questions**
  - **Property 4: Questions are presented in selection order**
  - **Validates: Requirements 3.4, 3.5**

- [ ]* 3.2 Write property test for question formatting
  - **Property 5: Question expression format is correct**
  - **Validates: Requirements 4.2**

- [ ]* 3.3 Write property test for question timer
  - **Property 6: Question timer advances to next question on expiration**
  - **Property 7: Question timer initializes to 15 seconds**
  - **Validates: Requirements 4.4, 4.5**

- [x] 4. Implement Pumpkin data model and spawning
  - Create Pumpkin dataclass with position, number, is_correct, velocity fields
  - Create PumpkinManager class with spawn logic
  - Implement spawn_pumpkin() to create pumpkins with 80% correct / 20% incorrect distribution
  - Add pumpkin update() method to move pumpkins downward
  - Implement off-screen detection and removal
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7_

- [ ]* 4.1 Write property test for pumpkin spawning
  - **Property 8: Spawned pumpkins have assigned numbers**
  - **Property 9: Correct answer distribution is approximately 80%**
  - **Validates: Requirements 5.2, 5.3, 5.4**

- [ ]* 4.2 Write property test for pumpkin movement
  - **Property 10: Pumpkins move downward over time**
  - **Property 11: Off-screen pumpkins are removed**
  - **Validates: Requirements 5.6, 5.7**

- [x] 5. Integrate hand tracking and cursor control
  - Import HandTracker from kiro_interaction_kit
  - Initialize HandTracker in game initialization
  - Implement cursor position tracking from hand position
  - Map camera coordinates to screen coordinates
  - Implement cursor rendering (simple circle or crosshair)
  - _Requirements: 6.1, 6.2, 6.3, 6.4_

- [ ]* 5.1 Write property test for cursor tracking
  - **Property 12: Cursor position tracks hand position**
  - **Property 13: Cursor position persists without hand detection**
  - **Validates: Requirements 6.3, 6.4**

- [x] 6. Implement slice action and collision detection
  - Implement check_collision() in PumpkinManager to detect cursor-pumpkin overlap
  - Detect pinch gesture from HandTracker state
  - Implement slice action logic (check if pumpkin is correct/incorrect)
  - Create Effect dataclass for visual effects
  - Add effect spawning for pie slice (correct) and cursed pumpkin (incorrect)
  - Implement pumpkin removal on slice
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.6_

- [ ]* 6.1 Write property test for slice mechanics
  - **Property 14: Pinch gesture with collision triggers slice**
  - **Property 15: Sliced pumpkins are removed**
  - **Validates: Requirements 7.1, 7.3, 7.6**

- [x] 7. Implement scoring and lives system
  - Add score variable (initialize to 0)
  - Add lives variable (initialize to 3)
  - Implement score increment (+5) on correct slice
  - Implement life decrement (-1) on incorrect slice
  - Render score in top left corner with "Score:" label
  - Render heart icons for remaining lives
  - _Requirements: 7.5, 8.1, 8.2, 8.3, 9.1, 9.2, 9.3, 9.4_

- [ ]* 7.1 Write property test for scoring
  - **Property 16: Incorrect slice decrements lives**
  - **Property 17: Correct slice increments score**
  - **Property 18: Displayed score matches internal score**
  - **Validates: Requirements 7.5, 9.3, 9.4**

- [ ]* 7.2 Write property test for lives display
  - **Property 19: Displayed hearts match life count**
  - **Validates: Requirements 8.2**

- [x] 8. Implement game state machine
  - Create GameState enum (START, INSTRUCTIONS, GAMEPLAY, GAME_OVER)
  - Implement state transitions based on user input and game conditions
  - Add Enter key detection for state transitions
  - Implement countdown timer (10 seconds) for INSTRUCTIONS state
  - _Requirements: 1.1, 1.2, 1.3, 2.1, 2.2, 2.3, 2.4_

- [ ]* 8.1 Write property test for countdown
  - **Property 24: Countdown decrements each second**
  - **Property 25: State remains until Enter is pressed**
  - **Validates: Requirements 2.3, 1.2**

- [x] 9. Implement game over and restart logic
  - Detect game over conditions (10 questions complete OR lives = 0)
  - Transition to GAME_OVER state when conditions met
  - Stop pumpkin spawning in GAME_OVER state
  - Display "Hit enter to restart game" text on game over screen
  - Implement restart logic (reset score, lives, select new questions, transition to INSTRUCTIONS)
  - _Requirements: 10.1, 10.2, 10.3, 10.4, 11.1, 11.2, 11.3, 11.4, 11.5_

- [ ]* 9.1 Write property test for game over conditions
  - **Property 20: Game ends after 10 questions**
  - **Property 21: Game ends when lives reach zero**
  - **Property 22: No pumpkins spawn in game over state**
  - **Validates: Requirements 10.1, 10.2, 10.3**

- [ ]* 9.2 Write property test for restart functionality
  - **Property 23: Restart resets game state**
  - **Validates: Requirements 11.2, 11.3, 11.4, 11.5**

- [x] 10. Implement complete rendering system
  - Render appropriate background for each game state (START, INSTRUCTIONS, GAMEPLAY)
  - Render question expression at top of screen during GAMEPLAY
  - Render question timer during GAMEPLAY
  - Render all pumpkins with their number circles
  - Render cursor during GAMEPLAY
  - Render active effects (pie slice, cursed pumpkin)
  - Render countdown during INSTRUCTIONS
  - Render game over text and restart prompt
  - _Requirements: 1.1, 2.1, 4.1, 4.3, 6.1, 10.4, 11.1_

- [x] 11. Polish and final integration
  - Adjust pumpkin spawn rate for good gameplay feel
  - Adjust pumpkin fall speed for appropriate difficulty
  - Add visual polish (font sizes, colors, positioning)
  - Test complete game flow from start to game over to restart
  - Verify all assets display correctly
  - Add ESC key to quit game
  - _Requirements: All_

- [x] 12. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ]* 13. Create README documentation
  - Document game controls (hand gestures, Enter key, ESC key)
  - Document game rules and objectives
  - Document how to run the game
  - Include screenshots or gameplay description
