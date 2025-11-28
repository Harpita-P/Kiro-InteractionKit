# Kiro Motion Kit

A gesture recognition library for Python that enables touchless interaction with applications using computer vision.

## Overview

Kiro Motion Kit provides a framework for detecting both hand gestures and head poses via webcam and mapping them to game or application actions. The library is designed to be framework-agnostic but includes Pygame demo applications showing cursor control and on-screen keyboard interaction driven entirely by gestures.

## Available Gestures

### Face Gestures

Kiro Motion Kit supports facial expression detection:

#### 1. Blink
**Function:** `is_blink()`  
**Detection Logic:** Uses Eye Aspect Ratio (EAR) to detect eye closure. Detects when both eyes are closed by measuring the vertical distance between upper and lower eyelids relative to the horizontal distance. MediaPipe Face Mesh landmarks: Left eye (159, 145, 33, 133), Right eye (386, 374, 263, 362).

#### 2. Mouth Open
**Function:** `is_mouth_open()`  
**Detection Logic:** Uses Mouth Aspect Ratio (MAR) to detect mouth opening. Measures the vertical distance between upper lip (landmark 13) and lower lip (landmark 14) relative to the horizontal distance between left mouth corner (landmark 78) and right mouth corner (landmark 308). Returns true when MAR exceeds threshold (default 0.03).

#### 3. Smiling
**Function:** `is_smiling()`  
**Detection Logic:** Detects smile by measuring the upward movement of mouth corners relative to the mouth center. Checks if both left corner (landmark 61) and right corner (landmark 291) are elevated above the mouth center (average of landmarks 0 and 17) by more than the threshold (default 0.015).

### Hand Gestures

Kiro Motion Kit currently supports the following hand gestures:

### 1. Fist (Closed Hand)
**Function:** `is_hand_closed()`  
**Detection Logic:** Detects when the middle fingertip (landmark 12) is significantly lower than the base of the middle finger (landmark 9), indicating a closed fist.

### 2. Pinch
**Function:** `is_pinch_gesture()`  
**Detection Logic:** Measures the Euclidean distance between thumb tip (landmark 4) and index fingertip (landmark 8). Returns true when they are close together (within threshold).

### 3. Peace Sign
**Function:** `is_peace_sign()`  
**Detection Logic:** Detects when index and middle fingers are extended upward and separated (forming a "V"), while ring and pinky fingers are curled down.

### 4. Thumbs Up
**Function:** `is_thumbs_up()`  
**Detection Logic:** Detects when the thumb is extended upward while all other fingers (index, middle, ring, pinky) are curled down.

### 5. Rock Sign (Devil Horns)
**Function:** `is_rock_sign()`  
**Detection Logic:** Detects when index and pinky fingers are extended upward and separated, while middle and ring fingers are curled down.

### 6. Open Hand
**Function:** `is_open_hand()`  
**Detection Logic:** Detects when all fingers are extended above their PIP joints and spread apart horizontally (minimum spread threshold of 0.15).

### 7. Pointing
**Function:** `is_pointing()`  
**Detection Logic:** Detects when the index finger is extended upward while middle, ring, and pinky fingers are curled down.

### 8. OK Sign
**Function:** `is_ok_sign()`  
**Detection Logic:** Detects when thumb tip and index fingertip are touching (forming a circle), while middle, ring, and pinky fingers are extended upward.

### 9. Thumbs Down
**Function:** `is_thumbs_down()`  
**Detection Logic:** Detects when the thumb is extended downward while all other fingers (index, middle, ring, pinky) are curled down.

### Head Gestures

Kiro Motion Kit also supports head pose tracking:

#### 1. Nod Up
**Function:** `is_nod_up()`  
**Detection Logic:** Detects when head x-axis rotation exceeds 15 degrees (looking up).

#### 2. Nod Down
**Function:** `is_nod_down()`  
**Detection Logic:** Detects when head x-axis rotation is below -15 degrees (looking down).

#### 3. Turn Left
**Function:** `is_turn_left()`  
**Detection Logic:** Detects when head y-axis rotation is below -20 degrees (turning left).

#### 4. Turn Right
**Function:** `is_turn_right()`  
**Detection Logic:** Detects when head y-axis rotation exceeds 20 degrees (turning right).

#### 5. Tilt Left
**Function:** `is_tilt_left()`  
**Detection Logic:** Detects when head z-axis rotation is below -15 degrees (tilting left).

#### 6. Tilt Right
**Function:** `is_tilt_right()`  
**Detection Logic:** Detects when head z-axis rotation exceeds 15 degrees (tilting right).

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

```python
from kiro_motion_kit import HandInputManager, dispatch_gesture_events, get_event_bus
import cv2

# Initialize hand input manager
hand_input = HandInputManager()

# Set up event listeners
bus = get_event_bus()
bus.on("gesture.pinch.start", lambda data: print("Pinch detected!"))

# Process camera frames
cap = cv2.VideoCapture(0)
while True:
    success, frame = cap.read()
    if not success:
        break
    
    actions, annotated_frame = hand_input.update_from_frame(frame)
    dispatch_gesture_events(actions)
    
    # Your application logic here
    if actions.is_pinch:
        print(f"Cursor at: {actions.cursor_x}, {actions.cursor_y}")

cap.release()
hand_input.close()
```

## Demo Applications

Run the included demos to see gestures in action:

```bash
# Gesture-controlled circle with size/color changes
python demo-apps/demo_pygame_cursor.py

# On-screen keyboard with pinch-to-type
python demo-apps/demo_pygame_keyboard.py
```

## Architecture

Kiro Motion Kit uses an event-driven layered architecture:

1. **Camera frame** → HandTracker → HandTrackingState
2. **HandTrackingState** → HandInputManager → HandInputSnapshot (with edge detection)
3. **HandInputSnapshot** → gesture_dispatcher → `gesture.*` events
4. **ActionMapper** subscribes to `gesture.*`, fires `game.*` events
5. **Game logic** subscribes to `game.*` events

This decoupling allows gesture detection to be independent of game logic.

## Event System

Each gesture fires start/end events:
- `gesture.closed.start` / `gesture.closed.end`
- `gesture.pinch.start` / `gesture.pinch.end`
- `gesture.peace.start` / `gesture.peace.end`
- `gesture.thumbs_up.start` / `gesture.thumbs_up.end`
- `gesture.rock_sign.start` / `gesture.rock_sign.end`
- `gesture.open_hand.start` / `gesture.open_hand.end`
- `gesture.pointing.start` / `gesture.pointing.end`
- `gesture.ok_sign.start` / `gesture.ok_sign.end`
- `gesture.thumbs_down.start` / `gesture.thumbs_down.end`

Map these to custom application actions using the ActionMapper.

## Requirements

- Python 3.x
- mediapipe
- opencv-python
- pygame (for demos)
- pyautogui (for system-level automation)

## License

See LICENSE file for details.
