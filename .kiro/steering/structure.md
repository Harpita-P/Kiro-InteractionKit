# Project Structure

## Core Package: `kiro_motion_kit/`

The main library organized into modular components:

### Controllers: `controllers/`
Low-level tracking using MediaPipe:
- `hand_controller.py`: Hand tracking
  - `HandTracker`: Processes camera frames, detects hand landmarks
  - `HandTrackingState`: Raw hand state (position, gestures detected)
- `head_controller.py`: Head pose tracking using MediaPipe Face Mesh
  - `HeadTracker`: Processes camera frames, detects head orientation
  - `HeadTrackingState`: Raw head pose state (x-axis, y-axis, z-axis rotation angles)
- `face_controller.py`: Face tracking using MediaPipe Face Mesh
  - `FaceTracker`: Processes camera frames, detects facial expressions
  - `FaceTrackingState`: Raw face state (blink, mouth open, smiling)

### Utilities: `utils/`
Helper functions for common tasks:
- `debug_view.py`: Camera feed rendering for Pygame

### Gesture Detection: `gestures/`
Modular gesture recognition functions organized by type:

#### Hand Gestures: `gestures/hand_gestures/`
- **Naming Convention**: Each gesture file must be prefixed with `HA` and a unique number: `HA1_gesture_name.py`, `HA2_gesture_name.py`, etc.
- Examples: `HA1_fist.py`, `HA2_pinch.py`, `HA3_peace.py`, `HA4_thumbs_up.py`, `HA5_rock_sign.py`
- Pure functions that analyze hand landmarks
- When creating new hand gestures, use the next available HA number in sequence

#### Head Gestures: `gestures/head_gestures/`
- **Naming Convention**: Each head gesture file must be prefixed with `HE` and a unique number: `HE1_gesture_name.py`, `HE2_gesture_name.py`, etc.
- Examples: `HE1_nod_up.py`, `HE2_nod_down.py`, `HE3_turn_left.py`, `HE4_turn_right.py`
- Pure functions that analyze head pose angles (x-axis, y-axis, z-axis)
- When creating new head gestures, use the next available HE number in sequence

#### Face Gestures: `gestures/face_gestures/`
- **Naming Convention**: Each face gesture file must be prefixed with `FA` and a unique number: `FA1_gesture_name.py`, `FA2_gesture_name.py`, etc.
- Examples: `FA1_blink.py`, `FA2_mouth_open.py`, `FA3_smiling.py`
- Pure functions that analyze face mesh landmarks (468 points from MediaPipe Face Mesh)
- When creating new face gestures, use the next available FA number in sequence



## Test Applications: `tests/`

Simple CV test demos for testing gesture detection:
- `CV-Test-Head.py`: Head gesture testing with visual feedback
- `CV-Test-Hands.py`: Hand gesture testing (create when needed)
- `CV-Test-Face.py`: Face gesture testing (create when needed)

## Games: `my_apps/`

User-created games using the Kiro Motion Kit framework. Each game should be in its own subdirectory.

**Example Games:**
- `cursor-demo/` - Hand gesture-controlled circle demo
- `keyboard-demo/` - On-screen keyboard with pinch-to-type

**Game Structure:**
Each game folder should contain:
- `main.py` - Entry point
- `README.md` - Game documentation
- Game-specific assets, mappings, or utilities as needed

**Important:** All game-specific code (assets, mappings, utilities) must be created within the game's folder under `my_apps/`. The core `kiro_motion_kit/` library should remain game-agnostic.

## Architecture Pattern

**Direct Controller Architecture:**
1. Camera frame → Tracker (Hand/Head/Face) → TrackingState
2. TrackingState contains gesture detection results as boolean flags
3. Application reads state directly and implements game logic

This direct approach keeps the library lean and focused on gesture detection. Applications can implement their own edge detection, events, or action mapping as needed.
