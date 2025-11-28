# Technology Stack

## Core Dependencies

- **mediapipe**: Hand tracking and landmark detection
- **opencv-python**: Camera capture and image processing
- **pygame**: Demo applications and UI rendering
- **pyautogui**: System-level keyboard/mouse automation

## Python Version

Python 3.x (uses dataclasses, type hints)

## Common Commands

### Running Demo Applications

```bash
# From project root
python demo-apps/demo_pygame_cursor.py
python demo-apps/demo_pygame_keyboard.py
```

### Installing Dependencies

```bash
pip install -r requirements.txt
```

## Build System

No build system required - pure Python package with direct imports.
