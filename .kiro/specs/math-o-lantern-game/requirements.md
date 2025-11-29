# Requirements Document

## Introduction

Math-O-Lantern is a gesture-controlled educational game that combines hand tracking technology with timed mathematics practice. Players use hand gestures to slice falling pumpkins that display answers to math problems, creating an engaging way to practice addition and subtraction skills. The game leverages the Kiro InteractionKit framework for hand tracking and gesture recognition, specifically using pinch gestures for interaction.

## Glossary

- **Math-O-Lantern System**: The complete gesture-controlled math game application
- **Player**: The user interacting with the game through hand gestures
- **Question Bank**: A collection of 50 pre-defined addition and subtraction problems
- **Game Session**: A single playthrough consisting of 10 randomly selected questions
- **Pumpkin**: A falling game object that displays a numerical answer
- **Cursor**: A visual indicator showing the tracked hand position on screen
- **Pinch Gesture**: A hand gesture where thumb and index finger tips come together, detected by the HandTracker
- **Slice Action**: The act of selecting a pumpkin by performing a pinch gesture while the cursor overlaps it
- **Correct Pumpkin**: A pumpkin displaying the correct answer to the current question
- **Incorrect Pumpkin**: A pumpkin displaying an incorrect answer to the current question
- **Life**: A unit representing player health, displayed as a heart icon (maximum 3)
- **Question Timer**: A 15-second countdown for each question
- **Start Screen**: The initial game screen displayed on launch
- **How-to-Play Screen**: An instructional screen with a 10-second countdown before gameplay
- **Game Background**: The background image used during active gameplay
- **Pumpkin Pie Slice**: A visual effect image displayed when a correct pumpkin is sliced
- **Cursed Pumpkin Effect**: A visual effect image displayed when an incorrect pumpkin is sliced
- **Score**: A numerical value representing the Player's performance, incremented by 5 for each correct answer
- **Game Over Screen**: The screen displayed when a Game Session ends

## Requirements

### Requirement 1

**User Story:** As a player, I want to see a start screen when I launch the game, so that I can prepare before beginning gameplay.

#### Acceptance Criteria

1. WHEN the Math-O-Lantern System launches THEN the Math-O-Lantern System SHALL display the start screen image as the background
2. WHILE the start screen is displayed THEN the Math-O-Lantern System SHALL wait for the Enter key press
3. WHEN the Player presses the Enter key on the start screen THEN the Math-O-Lantern System SHALL transition to the how-to-play screen

### Requirement 2

**User Story:** As a player, I want to see instructions and a countdown before gameplay starts, so that I understand how to play and can prepare myself.

#### Acceptance Criteria

1. WHEN the how-to-play screen is displayed THEN the Math-O-Lantern System SHALL show the how-to-play background image
2. WHEN the how-to-play screen is displayed THEN the Math-O-Lantern System SHALL display a countdown starting at 10 seconds
3. WHILE the countdown is active THEN the Math-O-Lantern System SHALL decrement the displayed number by 1 each second
4. WHEN the countdown reaches 0 THEN the Math-O-Lantern System SHALL transition to the main gameplay screen with the game background image

### Requirement 3

**User Story:** As a player, I want to be presented with random math problems from a question bank, so that each game session provides variety and replayability.

#### Acceptance Criteria

1. THE Math-O-Lantern System SHALL maintain a question bank containing exactly 50 math problems
2. THE Math-O-Lantern System SHALL include only addition and subtraction problems in the question bank
3. THE Math-O-Lantern System SHALL use numbers up to 4 digits in the question bank problems
4. WHEN a Game Session begins THEN the Math-O-Lantern System SHALL randomly select 10 unique questions from the question bank
5. WHEN a Game Session begins THEN the Math-O-Lantern System SHALL present the selected questions in sequence

### Requirement 4

**User Story:** As a player, I want to see the current math problem displayed at the top of the screen, so that I know which answer to look for on the pumpkins.

#### Acceptance Criteria

1. WHEN a question is active THEN the Math-O-Lantern System SHALL display the math expression at the top of the screen
2. THE Math-O-Lantern System SHALL format the math expression as "a + b = ?" or "a - b = ?"
3. WHEN a question is active THEN the Math-O-Lantern System SHALL display the Question Timer showing remaining seconds
4. WHEN the Question Timer reaches 0 seconds THEN the Math-O-Lantern System SHALL advance to the next question
5. THE Math-O-Lantern System SHALL set each Question Timer to 15 seconds

### Requirement 5

**User Story:** As a player, I want pumpkins with numbers to fall continuously across the screen, so that I have targets to interact with during gameplay.

#### Acceptance Criteria

1. WHILE a question is active THEN the Math-O-Lantern System SHALL spawn pumpkins continuously
2. WHEN a Pumpkin is spawned THEN the Math-O-Lantern System SHALL display a number in a small circle attached to the Pumpkin
3. WHEN a Pumpkin is spawned THEN the Math-O-Lantern System SHALL assign either the correct answer or an incorrect answer to the Pumpkin
4. THE Math-O-Lantern System SHALL assign the correct answer to approximately 80 percent of spawned pumpkins
5. THE Math-O-Lantern System SHALL assign incorrect answers to approximately 20 percent of spawned pumpkins
6. WHILE a Pumpkin exists THEN the Math-O-Lantern System SHALL move the Pumpkin downward across the screen
7. WHEN a Pumpkin reaches the bottom of the screen THEN the Math-O-Lantern System SHALL remove the Pumpkin from the game

### Requirement 6

**User Story:** As a player, I want to control a cursor with my hand position, so that I can target pumpkins for slicing.

#### Acceptance Criteria

1. WHEN the main gameplay is active THEN the Math-O-Lantern System SHALL display a Cursor on screen
2. WHILE the main gameplay is active THEN the Math-O-Lantern System SHALL track the Player hand position using the HandTracker
3. WHEN the HandTracker detects a hand THEN the Math-O-Lantern System SHALL update the Cursor position to match the hand position
4. WHEN the HandTracker does not detect a hand THEN the Math-O-Lantern System SHALL maintain the Cursor at its last known position

### Requirement 7

**User Story:** As a player, I want to slice pumpkins by performing a pinch gesture when my cursor is over them, so that I can select answers to the math problems.

#### Acceptance Criteria

1. WHEN the Player performs a Pinch Gesture AND the Cursor overlaps a Pumpkin THEN the Math-O-Lantern System SHALL execute a Slice Action on that Pumpkin
2. WHEN a Slice Action is executed on a Correct Pumpkin THEN the Math-O-Lantern System SHALL display the Pumpkin Pie Slice image at the Pumpkin location
3. WHEN a Slice Action is executed on a Correct Pumpkin THEN the Math-O-Lantern System SHALL remove the Pumpkin from the game
4. WHEN a Slice Action is executed on an Incorrect Pumpkin THEN the Math-O-Lantern System SHALL display the Cursed Pumpkin Effect image at the Pumpkin location
5. WHEN a Slice Action is executed on an Incorrect Pumpkin THEN the Math-O-Lantern System SHALL decrement the Player Life count by 1
6. WHEN a Slice Action is executed on an Incorrect Pumpkin THEN the Math-O-Lantern System SHALL remove the Pumpkin from the game

### Requirement 8

**User Story:** As a player, I want to see my remaining lives displayed as heart icons, so that I know how many mistakes I can make before the game ends.

#### Acceptance Criteria

1. WHEN the main gameplay begins THEN the Math-O-Lantern System SHALL initialize the Player Life count to 3
2. WHILE the main gameplay is active THEN the Math-O-Lantern System SHALL display heart icons representing the current Life count
3. WHEN the Player Life count changes THEN the Math-O-Lantern System SHALL update the displayed heart icons to reflect the current count

### Requirement 9

**User Story:** As a player, I want to earn points for correct answers, so that I can track my performance during the game.

#### Acceptance Criteria

1. WHEN the main gameplay begins THEN the Math-O-Lantern System SHALL initialize the Score to 0
2. WHILE the main gameplay is active THEN the Math-O-Lantern System SHALL display the Score in the top left corner with the text "Score:"
3. WHEN a Slice Action is executed on a Correct Pumpkin THEN the Math-O-Lantern System SHALL increment the Score by 5 points
4. WHEN the Score changes THEN the Math-O-Lantern System SHALL update the displayed Score value

### Requirement 10

**User Story:** As a player, I want the game to end when I complete all questions or lose all lives, so that I have clear win and loss conditions.

#### Acceptance Criteria

1. WHEN all 10 questions have been presented THEN the Math-O-Lantern System SHALL end the Game Session
2. WHEN the Player Life count reaches 0 THEN the Math-O-Lantern System SHALL end the Game Session
3. WHEN the Game Session ends THEN the Math-O-Lantern System SHALL stop spawning pumpkins
4. WHEN the Game Session ends THEN the Math-O-Lantern System SHALL display the Game Over Screen

### Requirement 11

**User Story:** As a player, I want to restart the game after it ends, so that I can play again without relaunching the application.

#### Acceptance Criteria

1. WHEN the Game Over Screen is displayed THEN the Math-O-Lantern System SHALL show the text "Hit enter to restart game"
2. WHEN the Player presses the Enter key on the Game Over Screen THEN the Math-O-Lantern System SHALL reset the Score to 0
3. WHEN the Player presses the Enter key on the Game Over Screen THEN the Math-O-Lantern System SHALL reset the Player Life count to 3
4. WHEN the Player presses the Enter key on the Game Over Screen THEN the Math-O-Lantern System SHALL select 10 new random questions from the question bank
5. WHEN the Player presses the Enter key on the Game Over Screen THEN the Math-O-Lantern System SHALL transition to the how-to-play screen

### Requirement 12

**User Story:** As a player, I want the game to use the provided asset images, so that the game has consistent and appropriate visual presentation.

#### Acceptance Criteria

1. THE Math-O-Lantern System SHALL use the start-game-screen.png asset for the Start Screen
2. THE Math-O-Lantern System SHALL use the how-to-play.png asset for the How-to-Play Screen
3. THE Math-O-Lantern System SHALL use the game-background.png asset for the Game Background
4. THE Math-O-Lantern System SHALL use the pumpkin.png asset for Pumpkin objects
5. THE Math-O-Lantern System SHALL use the slice-effect.png asset for the Pumpkin Pie Slice effect
6. THE Math-O-Lantern System SHALL use the cursed-pumpkin-effect.png asset for the Cursed Pumpkin Effect
7. THE Math-O-Lantern System SHALL use the heart.png asset for Life display icons
