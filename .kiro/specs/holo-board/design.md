# Design Document: Holo-Board

## Overview

Holo-Board is a gesture-controlled transparent whiteboard recording application built using the Kiro InteractionKit framework. The application creates an immersive drawing experience by overlaying a transparent drawing canvas on top of a live webcam feed, allowing users to draw in mid-air using hand gestures. The system captures the combined output (webcam + drawings) along with audio into a video file.

The application follows a direct controller architecture where hand gestures control drawing state, pen color, and canvas operations. Video recording is managed through OpenCV's VideoWriter with audio capture handled by PyAudio, synchronized and muxed using FFmpeg.

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Holo-Board Application                   │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │   Gesture    │    │   Drawing    │    │  Recording   │  │
│  │  Controller  │───▶│   Manager    │───▶│   Manager    │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│         │                    │                    │          │
│         │                    │                    │          │
│  ┌──────▼──────┐    ┌───────▼──────┐    ┌────────▼──────┐ │
│  │ HandTracker │    │ Pygame Canvas│    │ Video/Audio   │ │
│  │  (MediaPipe)│    │   Renderer   │    │   Capture     │ │
│  └─────────────┘    └──────────────┘    └───────────────┘ │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Component Interaction Flow

1. **Input Processing**: HandTracker processes webcam frames and detects hand gestures
2. **State Management**: Gesture Controller interprets gestures and updates application state
3. **Drawing Operations**: Drawing Manager maintains the drawing layer and renders strokes
4. **Display Rendering**: Pygame composites webcam feed with drawing layer
5. **Recording Pipeline**: Recording Manager captures frames and audio, muxes into video file

## Components and Interfaces

### 1. Main Application (`main.py`)

**Responsibilities:**
- Initialize Pygame window and camera
- Coordinate all subsystems (gesture, drawing, recording, UI)
- Main event loop and frame rendering
- Handle user input (mouse clicks on UI buttons)

**Key Methods:**
- `__init__()`: Initialize all subsystems
- `run()`: Main game loop
- `handle_events()`: Process Pygame events
- `update()`: Update all subsystems each frame
- `render()`: Composite and display all layers

### 2. Gesture Controller

**Responsibilities:**
- Process hand tracking state from HandTracker
- Detect gesture transitions (edge detection)
- Map gestures to application commands
- Maintain pen state (active/inactive)

**Key Attributes:**
- `hand_tracker`: HandTracker instance
- `pen_active`: Boolean indicating if pen is drawing
- `prev_gestures`: Previous frame gesture state for edge detection

**Key Methods:**
- `process_frame(frame)`: Process camera frame and return tracking state
- `update_pen_state(state)`: Update pen active/inactive based on gestures
- `get_pen_position(state)`: Extract index fingertip coordinates
- `detect_gesture_events(state)`: Detect gesture transitions (fist, peace)

**Gesture Mappings:**
- Pinch → Activate pen (start drawing)
- Open Hand → Deactivate pen (stop drawing)
- Fist → Clear canvas (edge-triggered)
- Peace → Cycle pen color (edge-triggered)

### 3. Drawing Manager

**Responsibilities:**
- Maintain drawing layer as Pygame surface with alpha channel
- Render continuous line strokes
- Handle pen color cycling
- Clear canvas operations

**Key Attributes:**
- `drawing_surface`: Pygame surface with SRCALPHA for transparency
- `current_color`: Current pen color (RGB tuple)
- `color_palette`: List of available colors
- `color_index`: Current position in color palette
- `last_pen_position`: Previous pen position for line continuity
- `pen_thickness`: Line width in pixels

**Key Methods:**
- `draw_stroke(start_pos, end_pos, color)`: Draw line segment
- `cycle_color()`: Advance to next color in palette
- `clear_canvas()`: Erase all drawing content
- `get_drawing_surface()`: Return current drawing layer for rendering

**Color Palette:**
- Red: (255, 69, 58)
- Green: (52, 199, 89)
- Blue: (0, 122, 255)
- Yellow: (255, 214, 10)
- Purple: (191, 90, 242)

### 4. Recording Manager

**Responsibilities:**
- Capture video frames from composited display
- Capture audio from microphone
- Synchronize audio and video streams
- Encode and mux into output video file
- Manage recording state and UI indicators

**Key Attributes:**
- `is_recording`: Boolean indicating active recording session
- `video_writer`: OpenCV VideoWriter instance
- `audio_stream`: PyAudio stream for microphone capture
- `audio_frames`: Buffer for captured audio data
- `output_filename`: Generated filename for current recording
- `frame_count`: Number of frames captured
- `start_time`: Recording start timestamp

**Key Methods:**
- `start_recording(width, height, fps)`: Initialize recording session
- `capture_frame(frame)`: Add video frame to recording
- `capture_audio()`: Continuously capture audio in separate thread
- `stop_recording()`: Finalize and mux video file
- `generate_filename()`: Create unique timestamped filename
- `mux_audio_video()`: Combine video and audio using FFmpeg

**Recording Pipeline:**
1. Create temporary video file (no audio) using OpenCV VideoWriter
2. Capture audio in separate thread using PyAudio
3. On stop, use FFmpeg to mux video and audio into final MP4 file
4. Clean up temporary files

### 5. UI Manager

**Responsibilities:**
- Render on-screen UI elements
- Handle button click detection
- Display recording indicator (vinyl asset)
- Animate vinyl rotation during recording

**Key Attributes:**
- `record_button_image`: Loaded record button asset
- `vinyl_image`: Loaded vinyl indicator asset
- `record_button_rect`: Button position and hitbox
- `vinyl_rotation`: Current rotation angle for animation
- `vinyl_position`: Corner position for indicator

**Key Methods:**
- `draw_record_button(screen)`: Render record button
- `draw_vinyl_indicator(screen)`: Render spinning vinyl during recording
- `is_button_clicked(mouse_pos)`: Check if record button was clicked
- `update_vinyl_rotation()`: Increment rotation angle

**UI Layout:**
- Record button: Bottom-right corner (with padding)
- Vinyl indicator: Top-right corner (visible only during recording)
- Vinyl rotation speed: 2 degrees per frame (smooth continuous spin)

## Data Models

### HandGestureState

```python
@dataclass
class HandGestureState:
    """Current state of detected hand gestures."""
    is_present: bool
    pinch: bool
    open_hand: bool
    fist: bool
    peace: bool
    index_fingertip: tuple[int, int]  # (x, y) in screen coordinates
```

### PenState

```python
@dataclass
class PenState:
    """Current state of the drawing pen."""
    active: bool
    position: tuple[int, int]  # (x, y) in screen coordinates
    color: tuple[int, int, int]  # RGB
    thickness: int
```

### RecordingState

```python
@dataclass
class RecordingState:
    """Current state of video recording."""
    is_recording: bool
    frame_count: int
    duration: float  # seconds
    output_path: str
```


## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Drawing Control Properties

**Property 1: Pinch activates pen**
*For any* hand gesture state where pinch is detected, processing that state should result in the pen becoming active
**Validates: Requirements 1.1**

**Property 2: Non-pinch deactivates pen**
*For any* hand gesture state where pinch is not detected (either released or open hand shown), processing that state should result in the pen becoming inactive
**Validates: Requirements 1.4, 1.5**

**Property 3: Active pen creates connected strokes**
*For any* sequence of positions while pen is active, consecutive positions should be connected by visible line segments on the drawing surface
**Validates: Requirements 1.2, 1.3**

**Property 4: Inactive pen preserves canvas**
*For any* drawing surface state, when the pen is inactive, position changes should not modify the drawing surface content
**Validates: Requirements 2.1, 2.3**

**Property 5: Pen deactivation terminates stroke**
*For any* active pen state that transitions to inactive, the next pen activation should start a new stroke rather than connecting to the previous position
**Validates: Requirements 2.2**

### Canvas Operations Properties

**Property 6: Fist clears canvas**
*For any* drawing surface with content, detecting a fist gesture should result in an empty drawing surface
**Validates: Requirements 3.1**

**Property 7: Fist clears and deactivates**
*For any* active pen state, detecting a fist gesture should both clear the drawing surface and deactivate the pen
**Validates: Requirements 3.3**

### Color Management Properties

**Property 8: Peace cycles color with wraparound**
*For any* color index in the palette, detecting a peace gesture should advance to the next color, and when at the final color, should wrap to the first color
**Validates: Requirements 4.1, 4.2**

**Property 9: New strokes use current color**
*For any* pen stroke drawn after a color change, the stroke should be rendered in the new current color
**Validates: Requirements 4.3**

**Property 10: Color change preserves existing strokes**
*For any* drawing surface with existing strokes, changing the current pen color should not modify the colors of previously rendered strokes
**Validates: Requirements 4.4**

### Recording Properties

**Property 11: Button click toggles recording**
*For any* recording state, clicking the record button should toggle the recording state (not recording → recording, or recording → not recording)
**Validates: Requirements 6.1, 6.3**

**Property 12: Recording shows vinyl indicator**
*For any* frame during active recording, the vinyl indicator should be visible and its rotation angle should increase
**Validates: Requirements 6.4, 6.5**

**Property 13: Recording start initializes audio capture**
*For any* recording session initiation, the audio stream should be initialized and capturing from the microphone
**Validates: Requirements 7.1**

**Property 14: Recording stop creates output file**
*For any* recording session termination, an output video file should exist at the specified path on the filesystem
**Validates: Requirements 8.1**

**Property 15: Recording stop includes audio track**
*For any* recording session with audio capture, the finalized output video should contain an audio track with the captured audio data
**Validates: Requirements 7.3**

**Property 16: Multiple recordings generate unique filenames**
*For any* sequence of recording sessions, each session should generate a distinct filename that does not overwrite previous recordings
**Validates: Requirements 8.4**

## Error Handling

### Gesture Detection Errors

**No Hand Detected:**
- When no hand is present in frame, pen state should remain inactive
- Existing drawing content should be preserved
- UI should continue to function normally

**Ambiguous Gestures:**
- When multiple conflicting gestures are detected simultaneously, prioritize in order: fist (clear) > peace (color) > pinch (draw) > open hand (stop)
- Log ambiguous gesture detection for debugging

**Tracking Loss:**
- When hand tracking is lost mid-stroke, terminate the current stroke
- Deactivate pen state until tracking is reestablished
- Preserve existing drawing content

### Recording Errors

**Camera Access Failure:**
- Display error message to user
- Prevent recording session from starting
- Allow application to continue running for drawing functionality

**Microphone Access Failure:**
- Log warning message
- Continue with video-only recording
- Display notification that audio is unavailable

**Disk Space Insufficient:**
- Check available disk space before starting recording
- If insufficient space detected, prevent recording start and notify user
- If space runs out during recording, stop recording gracefully and save partial video

**File Write Errors:**
- If output file cannot be written, display error message
- Attempt to save to alternative location (temp directory)
- Preserve captured frames in memory buffer for retry

**FFmpeg Muxing Failure:**
- If audio/video muxing fails, save video-only file
- Log error details for debugging
- Notify user that audio could not be included

### Drawing Errors

**Surface Allocation Failure:**
- If drawing surface cannot be allocated (memory constraints), reduce surface size
- If still failing, disable drawing functionality and notify user
- Continue displaying webcam feed

**Invalid Pen Position:**
- If pen position is outside screen bounds, clamp to valid coordinates
- Continue drawing with clamped position
- Log out-of-bounds occurrences for debugging

## Testing Strategy

### Unit Testing

The Holo-Board application will use **pytest** as the unit testing framework. Unit tests will focus on:

**Gesture Controller Tests:**
- Test pen state transitions for each gesture type
- Test edge detection for fist and peace gestures
- Test pen position extraction from hand tracking state
- Verify gesture priority when multiple gestures detected

**Drawing Manager Tests:**
- Test stroke rendering with various positions and colors
- Test color cycling through the palette
- Test canvas clearing operations
- Test stroke continuity and termination
- Verify drawing surface state after operations

**Recording Manager Tests:**
- Test recording state transitions (start/stop)
- Test filename generation uniqueness
- Test file creation and cleanup
- Mock video writer and audio stream for isolated testing

**UI Manager Tests:**
- Test button click detection with various mouse positions
- Test vinyl rotation angle increments
- Test UI element positioning

### Property-Based Testing

The Holo-Board application will use **Hypothesis** as the property-based testing framework. Each property-based test will run a minimum of 100 iterations to ensure comprehensive coverage across random inputs.

**Property Test Requirements:**
- Each property-based test MUST be tagged with a comment explicitly referencing the correctness property from this design document
- Tag format: `# Feature: holo-board, Property {number}: {property_text}`
- Each correctness property MUST be implemented by a SINGLE property-based test
- Tests should use Hypothesis strategies to generate random but valid inputs

**Property Test Coverage:**
- Properties 1-10: Drawing and color management (test with random gesture sequences, positions, colors)
- Properties 11-16: Recording functionality (test with random recording durations, filenames, state transitions)

**Test Data Generators:**
- Hand gesture states with random combinations of gesture flags
- Random pen positions within screen bounds
- Random color indices and palette configurations
- Random recording session sequences

### Integration Testing

**End-to-End Drawing Flow:**
- Start application → perform gestures → verify drawing appears → clear canvas
- Test complete drawing session with multiple strokes and color changes

**End-to-End Recording Flow:**
- Start application → start recording → draw content → stop recording → verify output file
- Test recording with audio capture and muxing

**Gesture-to-Visual Feedback:**
- Verify that each gesture produces the expected visual result
- Test gesture transitions and state consistency

### Manual Testing

**Visual Quality:**
- Verify drawing appears natural and smooth
- Check transparency and layer compositing
- Verify colors are distinct and visible

**Recording Quality:**
- Verify output video plays correctly in media players
- Check audio/video synchronization
- Verify frame rate and resolution

**Gesture Responsiveness:**
- Test gesture detection accuracy with different hand sizes and positions
- Verify gesture response time feels immediate
- Test in various lighting conditions

## Implementation Notes

### Technology Stack

- **Python 3.x**: Core application language
- **Pygame**: Window management, rendering, and UI
- **OpenCV (cv2)**: Camera capture and video writing
- **MediaPipe**: Hand tracking (via Kiro InteractionKit)
- **PyAudio**: Microphone audio capture
- **FFmpeg**: Audio/video muxing (external process)
- **Hypothesis**: Property-based testing framework
- **pytest**: Unit testing framework

### Performance Considerations

**Frame Rate:**
- Target 30 FPS for smooth drawing and recording
- Optimize drawing operations to minimize per-frame overhead
- Use dirty rectangle optimization if performance issues arise

**Memory Management:**
- Drawing surface should be allocated once at startup
- Reuse video frame buffers where possible
- Clear audio buffer after muxing to prevent memory growth

**Threading:**
- Audio capture should run in separate thread to prevent blocking
- Use thread-safe queue for audio frame buffer
- Ensure proper synchronization between audio and video threads

### Asset Requirements

**Record Button (`Assets/recording-button.png`):**
- Transparent PNG with clear record icon
- Recommended size: 64x64 pixels
- Should be visually distinct and clickable

**Vinyl Indicator (`Assets/vinyl.png`):**
- Transparent PNG of vinyl record
- Recommended size: 48x48 pixels
- Should be recognizable when spinning

### File Output Specifications

**Output Video Format:**
- Container: MP4
- Video codec: H.264 (libx264)
- Audio codec: AAC
- Resolution: Match camera resolution (typically 640x480 or 1280x720)
- Frame rate: 30 FPS
- Filename pattern: `holo-board-recording-YYYYMMDD-HHMMSS.mp4`

### Coordinate System

**Screen Coordinates:**
- Origin (0, 0) at top-left corner
- X-axis increases rightward
- Y-axis increases downward
- Hand tracking coordinates are normalized [0, 1] and must be scaled to screen dimensions

**Layer Ordering (bottom to top):**
1. Webcam feed (background)
2. Drawing layer (transparent overlay)
3. UI elements (record button, vinyl indicator)

### Gesture Detection Tuning

**Pinch Detection:**
- Use existing `HA2_pinch.py` from Kiro InteractionKit
- May need to adjust threshold for sensitivity

**Open Hand Detection:**
- Use existing `HA6_open_hand.py` from Kiro InteractionKit

**Fist Detection:**
- Use existing `HA1_fist.py` from Kiro InteractionKit

**Peace Detection:**
- Use existing `HA3_peace.py` from Kiro InteractionKit

All gesture detection functions are already implemented in the Kiro InteractionKit and should be used directly without modification unless sensitivity tuning is required.
