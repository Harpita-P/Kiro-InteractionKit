# Implementation Plan: Holo-Board

- [x] 1. Set up project structure and core components
  - Create `my_apps/Holo-Board/` directory structure
  - Create `main.py` entry point with Pygame initialization
  - Set up camera capture using OpenCV
  - Initialize HandTracker from Kiro InteractionKit
  - Create basic window with webcam feed display
  - _Requirements: 5.1, 5.2_

- [x] 2. Implement Drawing Manager
  - Create `DrawingManager` class with transparent Pygame surface
  - Implement color palette with 5 colors (red, green, blue, yellow, purple)
  - Implement `draw_stroke()` method for line rendering between two points
  - Implement `cycle_color()` method to advance through color palette with wraparound
  - Implement `clear_canvas()` method to erase all drawing content
  - Add pen thickness configuration (default 5 pixels)
  - _Requirements: 1.2, 1.3, 3.1, 4.1, 4.2, 4.3, 4.4_

- [ ]* 2.1 Write property test for stroke continuity
  - **Property 3: Active pen creates connected strokes**
  - **Validates: Requirements 1.2, 1.3**

- [ ]* 2.2 Write property test for color cycling
  - **Property 8: Peace cycles color with wraparound**
  - **Validates: Requirements 4.1, 4.2**

- [ ]* 2.3 Write property test for canvas clearing
  - **Property 6: Fist clears canvas**
  - **Validates: Requirements 3.1**

- [ ]* 2.4 Write unit tests for Drawing Manager
  - Test stroke rendering with various positions
  - Test color palette cycling
  - Test canvas clear operation
  - _Requirements: 1.2, 1.3, 3.1, 4.1, 4.2_

- [x] 3. Implement Gesture Controller
  - Create `GestureController` class wrapping HandTracker
  - Implement gesture detection using Kiro InteractionKit gesture functions (pinch, open_hand, fist, peace)
  - Implement edge detection for fist and peace gestures (trigger only on transition)
  - Implement pen state management (active/inactive based on pinch)
  - Implement `get_pen_position()` to extract index fingertip coordinates and scale to screen space
  - Add gesture priority handling (fist > peace > pinch > open_hand)
  - _Requirements: 1.1, 1.4, 1.5, 3.1, 3.3, 4.1_

- [ ]* 3.1 Write property test for pinch activation
  - **Property 1: Pinch activates pen**
  - **Validates: Requirements 1.1**

- [ ]* 3.2 Write property test for pen deactivation
  - **Property 2: Non-pinch deactivates pen**
  - **Validates: Requirements 1.4, 1.5**

- [ ]* 3.3 Write property test for stroke termination
  - **Property 5: Pen deactivation terminates stroke**
  - **Validates: Requirements 2.2**

- [ ]* 3.4 Write property test for fist clearing and deactivating
  - **Property 7: Fist clears and deactivates**
  - **Validates: Requirements 3.3**

- [ ]* 3.5 Write unit tests for Gesture Controller
  - Test gesture edge detection
  - Test pen state transitions
  - Test pen position extraction and scaling
  - _Requirements: 1.1, 1.4, 1.5, 3.3_

- [x] 4. Integrate drawing with gesture control
  - Connect GestureController to DrawingManager in main loop
  - Implement drawing logic: when pen active and position changes, call `draw_stroke()`
  - Track previous pen position for stroke continuity
  - Handle pen activation (start new stroke) vs continuation (connect to previous)
  - Implement fist gesture → clear canvas action
  - Implement peace gesture → cycle color action
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 2.1, 2.2, 2.3, 3.1, 3.3, 4.1_

- [ ]* 4.1 Write property test for inactive pen preservation
  - **Property 4: Inactive pen preserves canvas**
  - **Validates: Requirements 2.1, 2.3**

- [ ]* 4.2 Write property test for new stroke color
  - **Property 9: New strokes use current color**
  - **Validates: Requirements 4.3**

- [ ]* 4.3 Write property test for existing stroke color preservation
  - **Property 10: Color change preserves existing strokes**
  - **Validates: Requirements 4.4**

- [x] 5. Implement UI Manager
  - Create `UIManager` class for on-screen UI elements
  - Load record button asset from `Assets/recording-button.png`
  - Load vinyl indicator asset from `Assets/vinyl.png`
  - Implement `draw_record_button()` to render button in bottom-right corner
  - Implement `is_button_clicked()` for click detection using mouse position
  - Implement `draw_vinyl_indicator()` to render spinning vinyl in top-right corner
  - Implement `update_vinyl_rotation()` to increment rotation angle (2 degrees per frame)
  - _Requirements: 6.1, 6.3, 6.4, 6.5_

- [ ]* 5.1 Write unit tests for UI Manager
  - Test button click detection with various mouse positions
  - Test vinyl rotation angle increments
  - Test UI element positioning
  - _Requirements: 6.1, 6.4, 6.5_

- [x] 6. Implement Recording Manager (video only)
  - Create `RecordingManager` class for video capture
  - Implement `start_recording()` to initialize OpenCV VideoWriter with H.264 codec
  - Implement `capture_frame()` to write Pygame surface to video file
  - Implement `stop_recording()` to finalize video file
  - Implement `generate_filename()` with timestamp pattern `holo-board-recording-YYYYMMDD-HHMMSS.mp4`
  - Add recording state tracking (is_recording, frame_count, start_time)
  - _Requirements: 6.1, 6.2, 6.3, 8.1, 8.2, 8.4_

- [ ]* 6.1 Write property test for recording toggle
  - **Property 11: Button click toggles recording**
  - **Validates: Requirements 6.1, 6.3**

- [ ]* 6.2 Write property test for unique filenames
  - **Property 16: Multiple recordings generate unique filenames**
  - **Validates: Requirements 8.4**

- [ ]* 6.3 Write property test for output file creation
  - **Property 14: Recording stop creates output file**
  - **Validates: Requirements 8.1**

- [ ]* 6.4 Write unit tests for Recording Manager
  - Test recording state transitions
  - Test filename generation uniqueness
  - Test file creation (with mocked VideoWriter)
  - _Requirements: 6.1, 6.3, 8.1, 8.4_

- [x] 7. Integrate recording with main application
  - Connect RecordingManager to main loop
  - Handle record button clicks to start/stop recording
  - Capture composited frame (webcam + drawing layer) each frame during recording
  - Show/hide vinyl indicator based on recording state
  - Update vinyl rotation during recording
  - Convert Pygame surface to OpenCV format for video writing
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

- [ ]* 7.1 Write property test for vinyl indicator visibility
  - **Property 12: Recording shows vinyl indicator**
  - **Validates: Requirements 6.4, 6.5**

- [x] 8. Add audio capture to Recording Manager
  - Install PyAudio dependency
  - Implement audio capture in separate thread using PyAudio
  - Create thread-safe queue for audio frame buffer
  - Start audio capture thread in `start_recording()`
  - Stop audio capture thread in `stop_recording()`
  - Save audio frames to temporary WAV file
  - Handle microphone access errors gracefully (continue with video-only)
  - _Requirements: 7.1, 7.2, 7.3, 7.4_

- [ ]* 8.1 Write property test for audio initialization
  - **Property 13: Recording start initializes audio capture**
  - **Validates: Requirements 7.1**

- [ ]* 8.2 Write unit tests for audio capture
  - Test audio stream initialization
  - Test audio buffer management
  - Test graceful handling of missing microphone
  - _Requirements: 7.1, 7.4_

- [x] 9. Implement audio/video muxing with FFmpeg
  - Implement `mux_audio_video()` method using subprocess to call FFmpeg
  - Combine temporary video file and audio file into final MP4 with AAC audio
  - Clean up temporary files after successful muxing
  - Handle FFmpeg errors gracefully (save video-only if muxing fails)
  - Update `stop_recording()` to call muxing after video finalization
  - _Requirements: 7.3, 8.1, 8.2_

- [ ]* 9.1 Write property test for audio track inclusion
  - **Property 15: Recording stop includes audio track**
  - **Validates: Requirements 7.3**

- [ ]* 9.2 Write integration tests for recording pipeline
  - Test complete recording flow: start → capture → stop → mux
  - Test video-only fallback when audio unavailable
  - Test FFmpeg muxing with sample audio/video files
  - _Requirements: 6.1, 6.2, 6.3, 7.1, 7.3, 8.1_

- [x] 10. Add error handling and edge cases
  - Add camera access failure handling with error message
  - Add disk space check before recording
  - Add file write error handling with fallback to temp directory
  - Add invalid pen position clamping to screen bounds
  - Add gesture ambiguity resolution with priority order
  - Add tracking loss handling (terminate stroke, deactivate pen)
  - _Requirements: All requirements (error handling)_

- [x] 11. Create assets and finalize UI
  - Ensure `Assets/recording-button.png` exists (64x64 transparent PNG)
  - Ensure `Assets/vinyl.png` exists (48x48 transparent PNG)
  - Adjust UI positioning and sizing for visual appeal
  - Test button click hitbox accuracy
  - Verify vinyl rotation smoothness
  - _Requirements: 6.1, 6.4, 6.5_

- [x] 12. Final integration and polish
  - Test complete application flow end-to-end
  - Verify drawing appears natural and smooth
  - Verify recording output plays correctly in media players
  - Test gesture responsiveness and accuracy
  - Optimize frame rate if needed (target 30 FPS)
  - Add README.md with usage instructions
  - _Requirements: All requirements_

- [x] 13. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.
