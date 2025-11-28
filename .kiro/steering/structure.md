# Project Structure

## Core Package: `kiro_motion_kit/`

The main library organized into modular components:

### Hand Tracking Layer
- `hand_controller.py`: Low-level hand tracking using MediaPipe
  - `HandTracker`: Processes camera frames, detects hand landmarks
  - `HandTrackingState`: Raw hand state (position, gestures detected)

### Head Tracking Layer
- `head_controller.py`: Low-level head pose tracking using MediaPipe Face Mesh
  - `HeadTracker`: Processes camera frames, detects head orientation
  - `HeadTrackingState`: Raw head pose state (x-axis, y-axis, z-axis rotation angles)

### Input Abstraction Layer
- `hand_input.py`: Game-friendly input adapter
  - `HandInputManager`: Converts tracking state to input actions
  - `HandInputSnapshot`: Frame-by-frame input with edge detection (pressed/released)

### Hand Gesture Detection: `hand_gestures/`
- Modular hand gesture recognition functions
- **Naming Convention**: Each gesture file must be prefixed with `HA` and a unique number: `HA1_gesture_name.py`, `HA2_gesture_name.py`, etc.
- Examples: `HA1_fist.py`, `HA2_pinch.py`, `HA3_peace.py`, `HA4_thumbs_up.py`, `HA5_rock_sign.py`
- Pure functions that analyze hand landmarks
- When creating new hand gestures, use the next available HA number in sequence

### Head Gesture Detection: `head_gestures/`
- Modular head pose recognition functions
- **Naming Convention**: Each head gesture file must be prefixed with `HE` and a unique number: `HE1_gesture_name.py`, `HE2_gesture_name.py`, etc.
- Examples: `HE1_nod_up.py`, `HE2_nod_down.py`, `HE3_turn_left.py`, `HE4_turn_right.py`
- Pure functions that analyze head pose angles (x-axis, y-axis, z-axis)
- When creating new head gestures, use the next available HE number in sequence

### Face Gesture Detection: `face_gestures/`
- Modular facial expression recognition functions
- **Naming Convention**: Each face gesture file must be prefixed with `FA` and a unique number: `FA1_gesture_name.py`, `FA2_gesture_name.py`, etc.
- Examples: `FA1_blink.py`, `FA2_mouth_open.py`, `FA3_smiling.py`
- Pure functions that analyze face mesh landmarks (468 points from MediaPipe Face Mesh)
- When creating new face gestures, use the next available FA number in sequence

### Event System: `events/`
- `event_bus.py`: Simple pub/sub event bus (singleton pattern)
- `gesture_dispatcher.py`: Translates input snapshots to `gesture.*` events

### Action Mapping
- `action_mapping.py`: Maps low-level `gesture.*` events to high-level `game.*` actions
- `mappings/`: Application-specific mapping configurations
  - `cursor_demo_mapping.py`
  - `keyboard_demo_mapping.py`

### Utilities
- `debug_view.py`: Camera feed rendering for Pygame
- `assets/`: Empty folders for audio, fonts, images

## Demo Applications: `demo-apps/`

Standalone Pygame applications demonstrating library usage:
- `demo_pygame_cursor.py`: Gesture-controlled circle with size/color changes
- `demo_pygame_keyboard.py`: On-screen keyboard with pinch-to-type

## Architecture Pattern

**Event-Driven Layered Architecture:**
1. Camera frame → HandTracker → HandTrackingState
2. HandTrackingState → HandInputManager → HandInputSnapshot (with edges)
3. HandInputSnapshot → gesture_dispatcher → `gesture.*` events
4. ActionMapper subscribes to `gesture.*`, fires `game.*` events
5. Game logic subscribes to `game.*` events

This decoupling allows gesture detection to be independent of game logic.
