# Requirements Document

## Introduction

Holo-Board is a gesture-controlled transparent whiteboard recording application that enables users to draw in mid-air while recording video. The application combines real-time webcam feed with a transparent drawing overlay, creating the illusion of drawing on glass in front of the camera. Users control drawing, color selection, and canvas clearing through hand gestures, while the application captures the combined video output with audio.

## Glossary

- **Holo-Board System**: The complete gesture-controlled whiteboard recording application
- **Drawing Layer**: A transparent overlay positioned above the webcam feed where pen strokes are rendered
- **Pen State**: The active or inactive status of the drawing tool, controlled by hand gestures
- **Pinch Gesture**: A hand gesture where the thumb and index finger tips are brought close together
- **Open Hand Gesture**: A hand gesture where all fingers are extended and separated
- **Fist Gesture**: A hand gesture where all fingers are curled into the palm
- **Peace Gesture**: A hand gesture where the index and middle fingers are extended in a V-shape
- **Index Fingertip**: The tip of the index finger used as the pen position when drawing is active
- **Recording Session**: A period during which the Holo-Board System captures video and audio output
- **Vinyl Indicator**: A spinning visual element displayed during active recording
- **Record Button**: An on-screen UI element that initiates or terminates a recording session
- **Output Video**: The final video file containing webcam feed, drawing overlay, and audio

## Requirements

### Requirement 1

**User Story:** As a user, I want to draw continuous lines by performing a pinch gesture, so that I can create drawings in mid-air that appear on the transparent overlay.

#### Acceptance Criteria

1. WHEN the user performs a pinch gesture, THEN the Holo-Board System SHALL activate the pen state and begin drawing
2. WHILE the pen state is active, THE Holo-Board System SHALL render continuous line segments following the index fingertip position
3. WHEN the index fingertip moves during active pen state, THEN the Holo-Board System SHALL connect the previous position to the current position with a visible line
4. WHEN the user releases the pinch gesture, THEN the Holo-Board System SHALL deactivate the pen state and cease drawing operations
5. WHEN the user performs an open hand gesture, THEN the Holo-Board System SHALL deactivate the pen state and cease drawing operations

### Requirement 2

**User Story:** As a user, I want to move my hand without drawing marks when the pen is inactive, so that I can reposition before starting a new stroke.

#### Acceptance Criteria

1. WHILE the pen state is inactive, THE Holo-Board System SHALL allow index fingertip movement without rendering any marks on the drawing layer
2. WHEN the pen state transitions from active to inactive, THEN the Holo-Board System SHALL terminate the current stroke and prevent connection to subsequent positions
3. WHILE the pen state is inactive, THE Holo-Board System SHALL maintain the existing drawing layer content without modification

### Requirement 3

**User Story:** As a user, I want to clear the entire drawing by performing a fist gesture, so that I can start fresh without manually erasing individual strokes.

#### Acceptance Criteria

1. WHEN the user performs a fist gesture, THEN the Holo-Board System SHALL remove all rendered content from the drawing layer immediately
2. WHEN the drawing layer is cleared, THEN the Holo-Board System SHALL preserve the webcam feed visibility
3. WHEN a fist gesture is detected during active pen state, THEN the Holo-Board System SHALL clear the drawing layer and deactivate the pen state

### Requirement 4

**User Story:** As a user, I want to cycle through different pen colors using a peace gesture, so that I can create multi-colored drawings.

#### Acceptance Criteria

1. WHEN the user performs a peace gesture, THEN the Holo-Board System SHALL advance to the next color in the predefined color sequence
2. WHEN the Holo-Board System reaches the final color in the sequence, THEN the Holo-Board System SHALL cycle back to the first color upon the next peace gesture
3. WHEN the pen color changes, THEN the Holo-Board System SHALL apply the new color to all subsequent pen strokes
4. WHEN the pen color changes, THEN the Holo-Board System SHALL preserve the colors of previously rendered strokes

### Requirement 5

**User Story:** As a user, I want to see the live webcam feed as the background, so that I appear in the video while drawing.

#### Acceptance Criteria

1. WHEN the Holo-Board System starts, THEN the Holo-Board System SHALL display the live webcam feed as the background layer
2. WHILE the Holo-Board System is running, THE Holo-Board System SHALL continuously update the webcam feed at a minimum rate of 24 frames per second
3. WHEN the drawing layer is rendered, THEN the Holo-Board System SHALL position it above the webcam feed with transparency preserved
4. WHEN no drawing content exists, THEN the Holo-Board System SHALL display the unobstructed webcam feed

### Requirement 6

**User Story:** As a user, I want to start and stop video recording using an on-screen button, so that I can capture my drawing session.

#### Acceptance Criteria

1. WHEN the user clicks the record button while not recording, THEN the Holo-Board System SHALL initiate a recording session
2. WHEN a recording session is initiated, THEN the Holo-Board System SHALL capture the combined webcam feed and drawing layer at a minimum rate of 24 frames per second
3. WHEN the user clicks the record button during an active recording session, THEN the Holo-Board System SHALL terminate the recording session and finalize the output video
4. WHEN a recording session is active, THEN the Holo-Board System SHALL display the vinyl indicator in a corner of the screen
5. WHEN the vinyl indicator is displayed, THEN the Holo-Board System SHALL rotate it continuously to indicate active recording

### Requirement 7

**User Story:** As a user, I want the recording to include my microphone audio, so that I can narrate or explain my drawings.

#### Acceptance Criteria

1. WHEN a recording session is initiated, THEN the Holo-Board System SHALL begin capturing audio from the default microphone input
2. WHILE a recording session is active, THE Holo-Board System SHALL synchronize audio capture with video frame capture
3. WHEN a recording session terminates, THEN the Holo-Board System SHALL encode the captured audio into the output video file
4. WHEN no microphone is available, THEN the Holo-Board System SHALL create an output video without audio track

### Requirement 8

**User Story:** As a user, I want to download the recorded video file after recording ends, so that I can save and share my drawing session.

#### Acceptance Criteria

1. WHEN a recording session terminates, THEN the Holo-Board System SHALL write the output video to a file on the local filesystem
2. WHEN the output video is written, THEN the Holo-Board System SHALL use a standard video format compatible with common media players
3. WHEN the output video is finalized, THEN the Holo-Board System SHALL make the file accessible to the user for download or playback
4. WHEN multiple recording sessions occur, THEN the Holo-Board System SHALL generate unique filenames to prevent overwriting previous recordings

### Requirement 9

**User Story:** As a user, I want the drawing to appear as if I'm writing on transparent glass in front of the camera, so that the experience feels natural and immersive.

#### Acceptance Criteria

1. WHEN pen strokes are rendered, THEN the Holo-Board System SHALL display them with sufficient opacity to be clearly visible against the webcam feed
2. WHEN the drawing layer is composited with the webcam feed, THEN the Holo-Board System SHALL preserve the transparency of undrawn areas
3. WHEN viewing the combined output, THEN the Holo-Board System SHALL maintain the spatial relationship where drawings appear in front of the user
4. WHEN pen strokes overlap, THEN the Holo-Board System SHALL render them with consistent visual blending
