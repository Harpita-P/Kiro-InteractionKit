#!/usr/bin/env python3
"""
Holo-Board: Gesture-Controlled Transparent Whiteboard Recording Application

A gesture-controlled drawing application that overlays a transparent drawing canvas
on top of a live webcam feed, allowing users to draw in mid-air using hand gestures.
"""

import os
import sys
import cv2
import pygame
import wave
import threading
import subprocess
import shutil
import tempfile
from queue import Queue
from datetime import datetime

# Try to import tkinter for file dialog, but handle gracefully if not available
try:
    import tkinter as tk
    from tkinter import filedialog
    TKINTER_AVAILABLE = True
except ImportError:
    TKINTER_AVAILABLE = False
    print("Warning: tkinter not available. Will use pygame-based file browser.")

# Try to import PyAudio, but handle gracefully if not available
try:
    import pyaudio
    PYAUDIO_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False
    print("Warning: PyAudio not available. Audio recording will be disabled.")

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from kiro_interaction_kit.controllers.hand_controller import HandTracker

# Constants
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
FPS = 30


class GestureController:
    """Manages gesture detection and pen state control."""
    
    def __init__(self, screen_width, screen_height):
        """
        Initialize the Gesture Controller.
        
        Args:
            screen_width: Width of the screen for coordinate scaling
            screen_height: Height of the screen for coordinate scaling
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Initialize HandTracker from Kiro InteractionKit
        self.hand_tracker = HandTracker()
        
        # Pen state management
        self.pen_active = False
        
        # Previous gesture states for edge detection
        self.prev_thumbs_up = False
        self.prev_rock_sign = False
        
        # Store current hand state
        self.current_hand_state = None
    
    def process_frame(self, frame):
        """
        Process camera frame and detect gestures.
        
        Args:
            frame: OpenCV BGR frame from camera
            
        Returns:
            Tuple of (annotated_frame, gesture_events)
            gesture_events is a dict with keys: 'fist_pressed', 'peace_pressed'
        """
        # Process frame with HandTracker
        annotated_frame, hand_state = self.hand_tracker.process_frame(frame)
        
        # Store current hand state for later access
        self.current_hand_state = hand_state
        
        # Detect gesture events (edge detection for fist and peace)
        gesture_events = self._detect_gesture_events(hand_state)
        
        # Update pen state based on gestures with priority handling
        self._update_pen_state(hand_state, gesture_events)
        
        return annotated_frame, gesture_events
    
    def _detect_gesture_events(self, hand_state):
        """
        Detect gesture transitions (edge detection).
        
        Args:
            hand_state: HandTrackingState from HandTracker
            
        Returns:
            Dict with 'thumbs_up_pressed' and 'rock_sign_pressed' boolean flags
        """
        events = {
            'thumbs_up_pressed': False,
            'rock_sign_pressed': False
        }
        
        if not hand_state.is_present:
            # Reset previous states when hand is not present
            self.prev_thumbs_up = False
            self.prev_rock_sign = False
            return events
        
        # Edge detection: trigger only on transition from False to True
        if hand_state.is_thumbs_up and not self.prev_thumbs_up:
            events['thumbs_up_pressed'] = True
        
        if hand_state.is_rock_sign and not self.prev_rock_sign:
            events['rock_sign_pressed'] = True
        
        # Update previous states
        self.prev_thumbs_up = hand_state.is_thumbs_up
        self.prev_rock_sign = hand_state.is_rock_sign
        
        return events
    
    def _is_pointing_simple(self, hand_state):
        """
        Simple pointing detection: index finger higher than all other fingers.
        
        Args:
            hand_state: HandTrackingState from HandTracker
            
        Returns:
            Boolean indicating if pointing gesture is detected
        """
        if not hand_state.is_present or hand_state.landmarks is None:
            return False
        
        landmarks = hand_state.landmarks
        
        # Get y-coordinates (lower y = higher on screen)
        index_tip_y = landmarks[8].y
        middle_tip_y = landmarks[12].y
        ring_tip_y = landmarks[16].y
        pinky_tip_y = landmarks[20].y
        thumb_tip_y = landmarks[4].y
        
        # Index finger should be higher (lower y value) than all other fingers
        return (index_tip_y < middle_tip_y and 
                index_tip_y < ring_tip_y and 
                index_tip_y < pinky_tip_y and 
                index_tip_y < thumb_tip_y)
    
    def _update_pen_state(self, hand_state, gesture_events):
        """
        Update pen active/inactive state based on gestures.
        
        Gesture priority (highest to lowest): rock_sign > thumbs_up > pointing > open_hand
        This priority order resolves gesture ambiguity when multiple gestures are detected.
        
        Args:
            hand_state: HandTrackingState from HandTracker
            gesture_events: Dict with gesture event flags
        """
        if not hand_state.is_present:
            # Deactivate pen when hand is not present (tracking loss handling)
            self.pen_active = False
            return
        
        # Priority 1: Rock sign clears and deactivates pen (highest priority)
        if gesture_events['rock_sign_pressed']:
            self.pen_active = False
            return
        
        # Priority 2: Thumbs up gesture (just for color cycling, doesn't affect pen state)
        # Thumbs up doesn't change pen state, so we skip it here
        
        # Priority 3: Pointing activates pen (using simple detection)
        if self._is_pointing_simple(hand_state):
            self.pen_active = True
            return
        
        # Priority 4: Open hand or pointing release deactivates pen (lowest priority)
        if hand_state.is_open_hand or not self._is_pointing_simple(hand_state):
            self.pen_active = False
    
    def get_pen_position(self, hand_state):
        """
        Extract index fingertip coordinates and scale to screen space.
        
        Args:
            hand_state: HandTrackingState from HandTracker
            
        Returns:
            Tuple (x, y) in screen coordinates, or None if hand not present
        """
        if not hand_state.is_present or hand_state.cursor_x is None or hand_state.cursor_y is None:
            return None
        
        # Scale normalized coordinates [0, 1] to screen space
        screen_x = int(hand_state.cursor_x * self.screen_width)
        screen_y = int(hand_state.cursor_y * self.screen_height)
        
        # Clamp to screen bounds to handle invalid positions
        screen_x = max(0, min(screen_x, self.screen_width - 1))
        screen_y = max(0, min(screen_y, self.screen_height - 1))
        
        return (screen_x, screen_y)
    
    def is_pen_active(self):
        """
        Check if pen is currently active.
        
        Returns:
            Boolean indicating pen active state
        """
        return self.pen_active
    
    def close(self):
        """Release HandTracker resources."""
        self.hand_tracker.close()


class DrawingManager:
    """Manages the transparent drawing layer and pen operations."""
    
    # Color palette (8 colors)
    COLOR_PALETTE = [
        (255, 69, 58),    # Red
        (0, 122, 255),    # Blue
        (52, 199, 89),    # Green
        (255, 149, 0),    # Orange
        (255, 214, 10),   # Yellow
        (191, 90, 242),   # Purple
        (255, 45, 85),    # Pink
        (0, 199, 190),    # Cyan
    ]
    
    def __init__(self, width, height, pen_thickness=5):
        """
        Initialize the Drawing Manager.
        
        Args:
            width: Width of the drawing surface
            height: Height of the drawing surface
            pen_thickness: Thickness of pen strokes in pixels (default: 5)
        """
        self.width = width
        self.height = height
        self.pen_thickness = pen_thickness
        
        # Create transparent drawing surface with alpha channel
        self.drawing_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        self.drawing_surface.fill((0, 0, 0, 0))  # Fully transparent
        
        # Color management
        self.color_index = 0
        self.current_color = self.COLOR_PALETTE[self.color_index]
        
        # Track last pen position for stroke continuity
        self.last_pen_position = None
    
    def draw_stroke(self, start_pos, end_pos, color=None):
        """
        Draw a line segment between two points.
        
        Args:
            start_pos: Tuple (x, y) for start position
            end_pos: Tuple (x, y) for end position
            color: Optional RGB tuple for line color (uses current_color if None)
        """
        if color is None:
            color = self.current_color
        
        # Draw line on the drawing surface
        pygame.draw.line(
            self.drawing_surface,
            color,
            start_pos,
            end_pos,
            self.pen_thickness
        )
    
    def cycle_color(self):
        """
        Advance to the next color in the palette with wraparound.
        
        Returns:
            The new current color (RGB tuple)
        """
        self.color_index = (self.color_index + 1) % len(self.COLOR_PALETTE)
        self.current_color = self.COLOR_PALETTE[self.color_index]
        return self.current_color
    
    def clear_canvas(self):
        """Erase all drawing content from the canvas."""
        self.drawing_surface.fill((0, 0, 0, 0))  # Fill with fully transparent
        self.last_pen_position = None  # Reset pen position tracking
    
    def get_drawing_surface(self):
        """
        Get the current drawing surface for rendering.
        
        Returns:
            Pygame surface containing the drawing layer
        """
        return self.drawing_surface
    
    def get_current_color(self):
        """
        Get the current pen color.
        
        Returns:
            RGB tuple of current color
        """
        return self.current_color


class UIManager:
    """Manages on-screen UI elements (record button and vinyl indicator)."""
    
    def __init__(self, screen_width, screen_height):
        """
        Initialize the UI Manager.
        
        Args:
            screen_width: Width of the screen
            screen_height: Height of the screen
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Load assets
        assets_dir = os.path.join(os.path.dirname(__file__), "Assets")
        
        # Load record button asset
        record_button_path = os.path.join(assets_dir, "recording-button.png")
        self.record_button_image = pygame.image.load(record_button_path)
        
        # Load vinyl indicator asset
        vinyl_path = os.path.join(assets_dir, "vinyl.png")
        self.vinyl_image = pygame.image.load(vinyl_path)
        
        # Record button positioning (bottom-right corner with padding)
        self.button_padding = 20
        button_width = self.record_button_image.get_width()
        button_height = self.record_button_image.get_height()
        
        button_x = screen_width - button_width - self.button_padding
        button_y = screen_height - button_height - self.button_padding
        
        self.record_button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
        
        # Vinyl indicator positioning (top-right corner with padding)
        self.vinyl_padding = 20
        vinyl_width = self.vinyl_image.get_width()
        vinyl_height = self.vinyl_image.get_height()
        
        vinyl_x = screen_width - vinyl_width - self.vinyl_padding
        vinyl_y = self.vinyl_padding
        
        self.vinyl_position = (vinyl_x, vinyl_y)
        
        # Vinyl rotation state
        self.vinyl_rotation = 0.0
    
    def draw_record_button(self, screen):
        """
        Render the record button in the bottom-right corner.
        
        Args:
            screen: Pygame surface to draw on
        """
        screen.blit(self.record_button_image, self.record_button_rect.topleft)
    
    def is_button_clicked(self, mouse_pos):
        """
        Check if the record button was clicked.
        
        Args:
            mouse_pos: Tuple (x, y) of mouse position
            
        Returns:
            Boolean indicating if button was clicked
        """
        return self.record_button_rect.collidepoint(mouse_pos)
    
    def draw_vinyl_indicator(self, screen):
        """
        Render the spinning vinyl indicator in the top-right corner.
        
        Args:
            screen: Pygame surface to draw on
        """
        # Rotate the vinyl image
        rotated_vinyl = pygame.transform.rotate(self.vinyl_image, self.vinyl_rotation)
        
        # Get the rect of the rotated image (centered on original position)
        rotated_rect = rotated_vinyl.get_rect(center=(
            self.vinyl_position[0] + self.vinyl_image.get_width() // 2,
            self.vinyl_position[1] + self.vinyl_image.get_height() // 2
        ))
        
        # Draw the rotated vinyl
        screen.blit(rotated_vinyl, rotated_rect.topleft)
    
    def update_vinyl_rotation(self):
        """
        Increment the vinyl rotation angle by 2 degrees per frame.
        """
        self.vinyl_rotation = (self.vinyl_rotation + 2) % 360


class RecordingManager:
    """Manages video and audio recording."""
    
    # Audio configuration
    AUDIO_FORMAT = pyaudio.paInt16 if PYAUDIO_AVAILABLE else None
    AUDIO_CHANNELS = 1  # Mono
    AUDIO_RATE = 44100  # 44.1 kHz sample rate
    AUDIO_CHUNK = 1024  # Frames per buffer
    
    def __init__(self, output_directory=None):
        """
        Initialize the Recording Manager.
        
        Args:
            output_directory: Directory where recordings will be saved. 
                            If None, uses the directory of the main script.
        """
        # Recording state
        self.is_recording = False
        self.video_writer = None
        self.output_filename = None
        self.frame_count = 0
        self.start_time = None
        
        # Audio capture state
        self.audio_stream = None
        self.audio_frames = Queue()  # Thread-safe queue for audio frames
        self.audio_thread = None
        self.audio_stop_event = threading.Event()
        self.audio_available = False
        self.temp_audio_filename = None
        
        # Output directory management
        if output_directory is None:
            # Default to the directory where the main script is located
            output_directory = os.path.dirname(os.path.abspath(__file__))
        self.output_directory = output_directory
        self.fallback_directory = tempfile.gettempdir()  # Fallback to temp directory
        
        # Initialize PyAudio if available
        self.pyaudio_instance = None
        if PYAUDIO_AVAILABLE:
            try:
                self.pyaudio_instance = pyaudio.PyAudio()
                self.audio_available = True
            except Exception as e:
                print(f"Warning: Failed to initialize PyAudio: {e}")
                self.audio_available = False
    
    def generate_filename(self, directory=None):
        """
        Generate a unique timestamped filename for the recording.
        
        Args:
            directory: Optional directory path for the file. If None, uses output_directory.
        
        Returns:
            String full path in format: directory/holo-board-recording-YYYYMMDD-HHMMSS.mp4
        """
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        filename = f"holo-board-recording-{timestamp}.mp4"
        
        if directory is None:
            directory = self.output_directory
        
        return os.path.join(directory, filename)
    
    def check_disk_space(self, directory, required_mb=100):
        """
        Check if there is sufficient disk space available.
        
        Args:
            directory: Directory path to check
            required_mb: Required space in megabytes (default: 100 MB)
        
        Returns:
            Boolean indicating if sufficient space is available
        """
        try:
            stat = shutil.disk_usage(directory)
            available_mb = stat.free / (1024 * 1024)  # Convert bytes to MB
            
            if available_mb < required_mb:
                print(f"Warning: Low disk space. Available: {available_mb:.1f} MB, Required: {required_mb} MB")
                return False
            
            return True
        except Exception as e:
            print(f"Warning: Could not check disk space: {e}")
            # If we can't check, assume it's okay and let the write fail naturally
            return True
    
    def _capture_audio(self):
        """
        Continuously capture audio in a separate thread.
        This method runs in a background thread and captures audio frames
        into the thread-safe queue until the stop event is set.
        """
        if not self.audio_available or self.audio_stream is None:
            return
        
        try:
            while not self.audio_stop_event.is_set():
                try:
                    # Read audio data from stream
                    audio_data = self.audio_stream.read(self.AUDIO_CHUNK, exception_on_overflow=False)
                    # Add to queue
                    self.audio_frames.put(audio_data)
                except Exception as e:
                    print(f"Error capturing audio frame: {e}")
                    break
        except Exception as e:
            print(f"Audio capture thread error: {e}")
    
    def _save_audio_to_wav(self):
        """
        Save captured audio frames to a temporary WAV file.
        
        Returns:
            String path to the temporary WAV file, or None if no audio was captured
        """
        if self.audio_frames.empty():
            return None
        
        try:
            # Generate temporary audio filename
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            
            # Try to save in the same directory as the video
            output_dir = os.path.dirname(self.output_filename) if self.output_filename else self.output_directory
            temp_audio_path = os.path.join(output_dir, f"temp-audio-{timestamp}.wav")
            
            # Open WAV file for writing
            with wave.open(temp_audio_path, 'wb') as wf:
                wf.setnchannels(self.AUDIO_CHANNELS)
                wf.setsampwidth(self.pyaudio_instance.get_sample_size(self.AUDIO_FORMAT))
                wf.setframerate(self.AUDIO_RATE)
                
                # Write all audio frames from queue
                while not self.audio_frames.empty():
                    audio_data = self.audio_frames.get()
                    wf.writeframes(audio_data)
            
            print(f"Audio saved to temporary file: {temp_audio_path}")
            return temp_audio_path
        except Exception as e:
            print(f"Error saving audio to WAV: {e}")
            # Try fallback to temp directory
            try:
                temp_audio_path = os.path.join(self.fallback_directory, f"temp-audio-{timestamp}.wav")
                with wave.open(temp_audio_path, 'wb') as wf:
                    wf.setnchannels(self.AUDIO_CHANNELS)
                    wf.setsampwidth(self.pyaudio_instance.get_sample_size(self.AUDIO_FORMAT))
                    wf.setframerate(self.AUDIO_RATE)
                    
                    # Write all audio frames from queue
                    while not self.audio_frames.empty():
                        audio_data = self.audio_frames.get()
                        wf.writeframes(audio_data)
                
                print(f"Audio saved to fallback directory: {temp_audio_path}")
                return temp_audio_path
            except Exception as e2:
                print(f"Error saving audio to fallback directory: {e2}")
                return None
    
    def mux_audio_video(self, video_path, audio_path, output_path):
        """
        Combine temporary video file and audio file into final MP4 with AAC audio using FFmpeg.
        
        Args:
            video_path: Path to the temporary video file (video only)
            audio_path: Path to the temporary audio file (WAV)
            output_path: Path for the final muxed output file
            
        Returns:
            Boolean indicating if muxing was successful
        """
        try:
            # Check if FFmpeg is available
            try:
                subprocess.run(['ffmpeg', '-version'], 
                             stdout=subprocess.PIPE, 
                             stderr=subprocess.PIPE, 
                             check=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                print("Warning: FFmpeg not found. Cannot mux audio and video.")
                print("Saving video-only file instead.")
                return False
            
            # Build FFmpeg command to mux audio and video
            # -i video_path: input video file
            # -i audio_path: input audio file
            # -c:v copy: copy video stream without re-encoding
            # -c:a aac: encode audio to AAC
            # -strict experimental: allow experimental AAC encoder if needed
            # -shortest: finish encoding when shortest input stream ends
            ffmpeg_command = [
                'ffmpeg',
                '-i', video_path,      # Input video
                '-i', audio_path,      # Input audio
                '-c:v', 'copy',        # Copy video codec (no re-encoding)
                '-c:a', 'aac',         # Encode audio to AAC
                '-b:a', '192k',        # Audio bitrate
                '-shortest',           # Match shortest stream duration
                '-y',                  # Overwrite output file if exists
                output_path            # Output file
            ]
            
            print(f"Muxing audio and video with FFmpeg...")
            
            # Run FFmpeg command
            result = subprocess.run(
                ffmpeg_command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=60  # 60 second timeout
            )
            
            if result.returncode == 0:
                print(f"Successfully muxed audio and video: {output_path}")
                return True
            else:
                print(f"FFmpeg muxing failed with return code {result.returncode}")
                print(f"Error: {result.stderr.decode('utf-8', errors='ignore')}")
                return False
                
        except subprocess.TimeoutExpired:
            print("Error: FFmpeg muxing timed out")
            return False
        except Exception as e:
            print(f"Error during audio/video muxing: {e}")
            return False
    
    def start_recording(self, width, height, fps):
        """
        Initialize recording session with OpenCV VideoWriter and audio capture.
        
        Args:
            width: Video frame width
            height: Video frame height
            fps: Frames per second for video
            
        Returns:
            Boolean indicating if recording started successfully
        """
        if self.is_recording:
            print("Recording already in progress")
            return False
        
        # Check disk space before starting recording
        if not self.check_disk_space(self.output_directory):
            print("Error: Insufficient disk space to start recording")
            return False
        
        # Try to generate filename in primary directory
        try:
            self.output_filename = self.generate_filename(self.output_directory)
            output_dir = self.output_directory
        except Exception as e:
            print(f"Warning: Could not use primary directory: {e}")
            print(f"Falling back to temp directory: {self.fallback_directory}")
            try:
                self.output_filename = self.generate_filename(self.fallback_directory)
                output_dir = self.fallback_directory
            except Exception as e2:
                print(f"Error: Could not generate filename in fallback directory: {e2}")
                return False
        
        # Check disk space in the chosen directory
        if not self.check_disk_space(output_dir):
            print("Error: Insufficient disk space in output directory")
            return False
        
        # Define codec (H.264)
        # Try different codec options for compatibility
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # MP4V codec (more compatible)
        # Alternative: fourcc = cv2.VideoWriter_fourcc(*'avc1')  # H.264 codec
        
        # Initialize VideoWriter with error handling
        try:
            self.video_writer = cv2.VideoWriter(
                self.output_filename,
                fourcc,
                fps,
                (width, height)
            )
            
            if not self.video_writer.isOpened():
                print(f"Failed to initialize VideoWriter for {self.output_filename}")
                self.video_writer = None
                
                # Try fallback directory if primary failed
                if output_dir != self.fallback_directory:
                    print(f"Trying fallback directory: {self.fallback_directory}")
                    self.output_filename = self.generate_filename(self.fallback_directory)
                    
                    self.video_writer = cv2.VideoWriter(
                        self.output_filename,
                        fourcc,
                        fps,
                        (width, height)
                    )
                    
                    if not self.video_writer.isOpened():
                        print(f"Failed to initialize VideoWriter in fallback directory")
                        self.video_writer = None
                        return False
                else:
                    return False
        except Exception as e:
            print(f"Error initializing VideoWriter: {e}")
            self.video_writer = None
            return False
        
        # Initialize audio capture if available
        if self.audio_available:
            try:
                # Open audio stream
                self.audio_stream = self.pyaudio_instance.open(
                    format=self.AUDIO_FORMAT,
                    channels=self.AUDIO_CHANNELS,
                    rate=self.AUDIO_RATE,
                    input=True,
                    frames_per_buffer=self.AUDIO_CHUNK
                )
                
                # Clear the audio frames queue
                while not self.audio_frames.empty():
                    self.audio_frames.get()
                
                # Reset stop event
                self.audio_stop_event.clear()
                
                # Start audio capture thread
                self.audio_thread = threading.Thread(target=self._capture_audio, daemon=True)
                self.audio_thread.start()
                
                print("Audio capture initialized")
            except Exception as e:
                print(f"Warning: Failed to initialize audio capture: {e}")
                print("Continuing with video-only recording")
                self.audio_stream = None
                self.audio_thread = None
        else:
            print("Audio not available, recording video only")
        
        # Update recording state
        self.is_recording = True
        self.frame_count = 0
        self.start_time = datetime.now()
        
        print(f"Recording started: {self.output_filename}")
        return True
    
    def capture_frame(self, frame):
        """
        Write a Pygame surface to the video file.
        
        Args:
            frame: Pygame surface to capture
            
        Returns:
            Boolean indicating if frame was captured successfully
        """
        if not self.is_recording or self.video_writer is None:
            return False
        
        try:
            # Convert Pygame surface to numpy array (RGB)
            frame_array = pygame.surfarray.array3d(frame)
            
            # Transpose from (width, height, 3) to (height, width, 3)
            frame_array = frame_array.transpose(1, 0, 2)
            
            # Convert RGB to BGR for OpenCV
            frame_bgr = cv2.cvtColor(frame_array, cv2.COLOR_RGB2BGR)
            
            # Write frame to video
            self.video_writer.write(frame_bgr)
            
            # Increment frame count
            self.frame_count += 1
            
            # Periodically check disk space (every 100 frames)
            if self.frame_count % 100 == 0:
                output_dir = os.path.dirname(self.output_filename)
                if not self.check_disk_space(output_dir, required_mb=50):
                    print("Warning: Low disk space during recording. Consider stopping soon.")
            
            return True
        except Exception as e:
            print(f"Error capturing frame: {e}")
            # If we encounter a write error, stop recording gracefully
            print("Stopping recording due to write error")
            self.stop_recording()
            return False
    
    def stop_recording(self):
        """
        Finalize and save the video file with audio.
        
        Returns:
            String path to the saved video file, or None if recording wasn't active
        """
        if not self.is_recording:
            print("No recording in progress")
            return None
        
        # Stop audio capture thread
        if self.audio_thread is not None:
            # Signal the audio thread to stop
            self.audio_stop_event.set()
            # Wait for thread to finish (with timeout)
            self.audio_thread.join(timeout=2.0)
            self.audio_thread = None
        
        # Close audio stream
        if self.audio_stream is not None:
            try:
                self.audio_stream.stop_stream()
                self.audio_stream.close()
            except Exception as e:
                print(f"Error closing audio stream: {e}")
            self.audio_stream = None
        
        # Save audio frames to temporary WAV file
        self.temp_audio_filename = None
        if self.audio_available and not self.audio_frames.empty():
            self.temp_audio_filename = self._save_audio_to_wav()
        
        # Finalize video file
        if self.video_writer is not None:
            self.video_writer.release()
            self.video_writer = None
        
        # Calculate recording duration
        if self.start_time is not None:
            duration = (datetime.now() - self.start_time).total_seconds()
            print(f"Recording stopped: {self.output_filename}")
            print(f"Duration: {duration:.2f}s, Frames: {self.frame_count}")
        
        # Store temporary video filename
        temp_video_filename = self.output_filename
        
        # Generate final output filename in the same directory
        output_dir = os.path.dirname(self.output_filename) if self.output_filename else self.output_directory
        try:
            final_output_filename = self.generate_filename(output_dir)
        except Exception as e:
            print(f"Error generating final filename: {e}")
            # Use the temp video filename as final if we can't generate a new one
            final_output_filename = temp_video_filename
        
        # Mux audio and video if audio was captured
        if self.temp_audio_filename and os.path.exists(self.temp_audio_filename):
            print("Muxing audio and video...")
            mux_success = self.mux_audio_video(
                temp_video_filename,
                self.temp_audio_filename,
                final_output_filename
            )
            
            if mux_success:
                # Muxing successful - clean up temporary files
                try:
                    if os.path.exists(temp_video_filename):
                        os.remove(temp_video_filename)
                        print(f"Cleaned up temporary video file: {temp_video_filename}")
                    if os.path.exists(self.temp_audio_filename):
                        os.remove(self.temp_audio_filename)
                        print(f"Cleaned up temporary audio file: {self.temp_audio_filename}")
                except Exception as e:
                    print(f"Warning: Failed to clean up temporary files: {e}")
                
                output_path = final_output_filename
            else:
                # Muxing failed - save video-only file
                print("Muxing failed. Saving video-only file.")
                # Keep the original video file
                output_path = temp_video_filename
                
                # Clean up audio file
                try:
                    if os.path.exists(self.temp_audio_filename):
                        os.remove(self.temp_audio_filename)
                        print(f"Cleaned up temporary audio file: {self.temp_audio_filename}")
                except Exception as e:
                    print(f"Warning: Failed to clean up audio file: {e}")
        else:
            # No audio captured - just use the video file
            print("No audio captured. Saving video-only file.")
            output_path = temp_video_filename
        
        # Reset recording state
        self.is_recording = False
        self.frame_count = 0
        self.start_time = None
        self.output_filename = None
        self.temp_audio_filename = None
        
        print(f"Final recording saved: {output_path}")
        return output_path
    
    def get_recording_state(self):
        """
        Get current recording state information.
        
        Returns:
            Dict with recording state information
        """
        return {
            'is_recording': self.is_recording,
            'frame_count': self.frame_count,
            'duration': (datetime.now() - self.start_time).total_seconds() if self.start_time else 0.0,
            'output_path': self.output_filename
        }
    
    def cleanup(self):
        """Release PyAudio resources."""
        # Stop recording if active
        if self.is_recording:
            self.stop_recording()
        
        # Terminate PyAudio
        if self.pyaudio_instance is not None:
            try:
                self.pyaudio_instance.terminate()
            except Exception as e:
                print(f"Error terminating PyAudio: {e}")
            self.pyaudio_instance = None


class HoloBoardApp:
    """Main application class for Holo-Board."""
    
    def __init__(self):
        """Initialize the Holo-Board application."""
        # Initialize Pygame
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Holo-Board - Gesture-Controlled Whiteboard")
        self.clock = pygame.time.Clock()
        
        # Load launch screen assets
        assets_dir = os.path.join(os.path.dirname(__file__), "Assets")
        self.launch_image = pygame.image.load(os.path.join(assets_dir, "Holo-Board-Launch.png"))
        self.start_button_image = pygame.image.load(os.path.join(assets_dir, "Start-Button.png"))
        
        # Start button animation
        self.button_scale = 1.0
        self.button_scale_direction = 1
        self.button_scale_speed = 0.015
        self.button_min_scale = 0.9
        self.button_max_scale = 1.1
        
        # App state
        self.app_started = False
        self.start_button_rect = None
        
        # These will be initialized after launch screen
        self.cap = None
        self.camera_width = None
        self.camera_height = None
        self.gesture_controller = None
        self.drawing_manager = None
        self.ui_manager = None
        self.recording_manager = None
        self.prev_pen_position = None
        self.smoothed_position = None
        self.smoothing_factor = 0.5
        self.annotation_image = None
        self.annotation_rect = None
    
    def _show_launch_screen(self):
        """Show launch screen and wait for start button click."""
        waiting = True
        
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    if self.start_button_rect and self.start_button_rect.collidepoint(mouse_pos):
                        return True
            
            # Draw launch screen
            self.screen.fill((0, 0, 0))
            
            # Scale down the launch image to 70% of its original size
            launch_scale = 0.7
            scaled_launch_width = int(self.launch_image.get_width() * launch_scale)
            scaled_launch_height = int(self.launch_image.get_height() * launch_scale)
            scaled_launch_image = pygame.transform.scale(self.launch_image, (scaled_launch_width, scaled_launch_height))
            
            # Draw scaled launch image (centered on screen)
            launch_rect = scaled_launch_image.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
            self.screen.blit(scaled_launch_image, launch_rect)
            
            # Animate start button (pulsing effect - growing and shrinking continuously)
            self.button_scale += self.button_scale_speed * self.button_scale_direction
            if self.button_scale >= self.button_max_scale:
                self.button_scale = self.button_max_scale
                self.button_scale_direction = -1
            elif self.button_scale <= self.button_min_scale:
                self.button_scale = self.button_min_scale
                self.button_scale_direction = 1
            
            # Scale down start button much smaller (base scale of 0.12 = 12% of original size)
            base_button_scale = 0.12
            final_button_scale = base_button_scale * self.button_scale
            button_width = int(self.start_button_image.get_width() * final_button_scale)
            button_height = int(self.start_button_image.get_height() * final_button_scale)
            scaled_button = pygame.transform.scale(self.start_button_image, (button_width, button_height))
            
            # Position: slightly right of center, very close to bottom
            button_x = (WINDOW_WIDTH - button_width) // 2 + 60  # Shifted 60px to the right
            button_y = WINDOW_HEIGHT - button_height - 10  # Very close to bottom
            self.start_button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
            
            self.screen.blit(scaled_button, (button_x, button_y))
            
            pygame.display.flip()
            self.clock.tick(FPS)
        
        return False
    
    def _initialize_camera_and_components(self):
        """Initialize camera and all components after launch screen."""
        camera_error = None
        
        try:
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                camera_error = "Camera device could not be opened. Please check if:\n" \
                              "  - A camera is connected to your computer\n" \
                              "  - Camera permissions are granted to this application\n" \
                              "  - No other application is using the camera"
                raise RuntimeError(camera_error)
            
            # Set camera resolution
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, WINDOW_WIDTH)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, WINDOW_HEIGHT)
            
            # Get actual camera resolution (may differ from requested)
            self.camera_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            self.camera_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            # Verify we can actually read a frame
            success, test_frame = self.cap.read()
            if not success or test_frame is None:
                camera_error = "Camera opened but cannot read frames. The camera may be in use by another application."
                raise RuntimeError(camera_error)
                
        except Exception as e:
            # Clean up and show error message
            if self.cap is not None:
                self.cap.release()
                self.cap = None
            
            # Display error message on screen
            self._show_error_message(camera_error if camera_error else str(e))
            pygame.quit()
            raise RuntimeError(f"Failed to initialize camera: {e}")
        
        # Initialize GestureController
        self.gesture_controller = GestureController(WINDOW_WIDTH, WINDOW_HEIGHT)
        
        # Initialize DrawingManager
        self.drawing_manager = DrawingManager(WINDOW_WIDTH, WINDOW_HEIGHT)
        
        # Initialize UIManager
        self.ui_manager = UIManager(WINDOW_WIDTH, WINDOW_HEIGHT)
        
        # Initialize RecordingManager with Recordings directory as output location
        holo_board_dir = os.path.dirname(os.path.abspath(__file__))
        recordings_dir = os.path.join(holo_board_dir, "Recordings")
        
        # Create Recordings directory if it doesn't exist
        if not os.path.exists(recordings_dir):
            try:
                os.makedirs(recordings_dir)
                print(f"Created Recordings directory: {recordings_dir}")
            except Exception as e:
                print(f"Warning: Could not create Recordings directory: {e}")
                recordings_dir = holo_board_dir  # Fallback to main directory
        
        self.recording_manager = RecordingManager(output_directory=recordings_dir)
        
        # Image annotation feature
        self._prompt_for_image_annotation()
        
        print(f"Holo-Board initialized")
        print(f"Window: {WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        print(f"Camera: {self.camera_width}x{self.camera_height}")
    
    def _show_error_message(self, message):
        """
        Display an error message on the Pygame screen.
        
        Args:
            message: Error message to display
        """
        # Fill screen with dark background
        self.screen.fill((40, 40, 40))
        
        # Render error message
        font = pygame.font.Font(None, 36)
        title_text = font.render("Error: Camera Access Failed", True, (255, 100, 100))
        title_rect = title_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 100))
        self.screen.blit(title_text, title_rect)
        
        # Render detailed message (split into lines)
        small_font = pygame.font.Font(None, 24)
        lines = message.split('\n')
        y_offset = WINDOW_HEIGHT // 2 - 20
        
        for line in lines:
            line_text = small_font.render(line.strip(), True, (200, 200, 200))
            line_rect = line_text.get_rect(center=(WINDOW_WIDTH // 2, y_offset))
            self.screen.blit(line_text, line_rect)
            y_offset += 30
        
        # Show exit instruction
        exit_text = small_font.render("Press ESC or close window to exit", True, (150, 150, 150))
        exit_rect = exit_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 50))
        self.screen.blit(exit_text, exit_rect)
        
        pygame.display.flip()
        
        # Wait for user to close
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        waiting = False
    
    def _prompt_for_image_annotation(self):
        """
        Open file picker to select an annotation image.
        User can press ESC to skip if they don't want an image.
        """
        if TKINTER_AVAILABLE:
            # Use tkinter file dialog for GUI file selection
            try:
                root = tk.Tk()
                root.withdraw()
                root.attributes('-topmost', True)
                
                # Set initial directory to Annotate folder
                annotate_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Annotate")
                if not os.path.exists(annotate_dir):
                    annotate_dir = os.path.dirname(os.path.abspath(__file__))
                
                # Open file dialog
                file_path = filedialog.askopenfilename(
                    title="Select an annotation image (or cancel to skip)",
                    filetypes=[
                        ("Image files", "*.png *.jpg *.jpeg"),
                        ("PNG files", "*.png"),
                        ("JPEG files", "*.jpg *.jpeg"),
                        ("All files", "*.*")
                    ],
                    initialdir=annotate_dir
                )
                
                root.destroy()
                
                if file_path and os.path.exists(file_path):
                    if file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
                        self._load_annotation_image(file_path)
                        print(f"✓ Loaded: {os.path.basename(file_path)}")
                    else:
                        print("✗ Error: Only PNG and JPG files are supported")
                else:
                    print("No image selected. Starting without annotation image.")
            except Exception as e:
                print(f"Error with file dialog: {e}")
                print("Starting without annotation image.")
        else:
            # Fallback: Use pygame-based file browser
            file_path = self._show_pygame_file_browser()
            
            if file_path and os.path.exists(file_path):
                if file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
                    self._load_annotation_image(file_path)
                    print(f"✓ Loaded: {os.path.basename(file_path)}")
                else:
                    print("✗ Error: Only PNG and JPG files are supported")
            else:
                print("No image selected. Starting without annotation image.")
    
    def _show_pygame_file_browser(self):
        """
        Show a modern pygame-based file browser for selecting images.
        Returns the selected file path or None if cancelled.
        """
        # Light theme with turquoise accents
        bg_color = (245, 248, 250)  # Light blue-gray background
        card_color = (255, 255, 255)  # White card
        item_color = (248, 250, 252)  # Very light gray for items
        item_hover = (235, 245, 250)  # Light blue-gray on hover
        selected_color = (0, 128, 128)  # Dark turquoise for selected
        text_primary = (40, 50, 60)  # Dark text
        text_secondary = (100, 110, 120)  # Medium gray text
        turquoise = (0, 128, 128)  # Dark turquoise accent
        shadow_color = (200, 210, 220)  # Subtle shadow
        
        # Start in the Annotate directory
        current_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Annotate")
        if not os.path.exists(current_dir):
            current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Get list of image files in current directory
        def get_image_files(directory):
            files = []
            try:
                for item in sorted(os.listdir(directory)):
                    full_path = os.path.join(directory, item)
                    if os.path.isfile(full_path) and item.lower().endswith(('.png', '.jpg', '.jpeg')):
                        files.append(item)
            except Exception as e:
                print(f"Error reading directory: {e}")
            return files
        
        files = get_image_files(current_dir)
        selected_index = 0 if files else -1
        scroll_offset = 0
        max_visible = 8
        
        browsing = True
        selected_file = None
        
        font_title = pygame.font.SysFont('Arial', 52, bold=True)
        font_subtitle = pygame.font.SysFont('Arial', 28)
        font_item = pygame.font.SysFont('Arial', 32)
        font_hint = pygame.font.SysFont('Arial', 22)
        
        # Animation
        hover_index = -1
        
        while browsing:
            mouse_pos = pygame.mouse.get_pos()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    browsing = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        browsing = False
                    elif event.key == pygame.K_UP and files:
                        selected_index = max(0, selected_index - 1)
                        if selected_index < scroll_offset:
                            scroll_offset = selected_index
                    elif event.key == pygame.K_DOWN and files:
                        selected_index = min(len(files) - 1, selected_index + 1)
                        if selected_index >= scroll_offset + max_visible:
                            scroll_offset = selected_index - max_visible + 1
                    elif event.key == pygame.K_RETURN and files and selected_index >= 0:
                        selected_file = os.path.join(current_dir, files[selected_index])
                        browsing = False
                elif event.type == pygame.MOUSEBUTTONDOWN and files:
                    # Check if clicked on a file item
                    if hover_index >= 0:
                        selected_index = hover_index
                        selected_file = os.path.join(current_dir, files[selected_index])
                        browsing = False
            
            # Draw light background
            self.screen.fill(bg_color)
            
            # Draw card shadow
            card_padding = 80
            shadow_rect = pygame.Rect(
                card_padding - 5,
                card_padding - 5,
                WINDOW_WIDTH - (card_padding - 5) * 2,
                WINDOW_HEIGHT - (card_padding - 5) * 2
            )
            self._draw_rounded_rect(self.screen, shadow_color, shadow_rect, radius=30)
            
            # Draw main card
            card_rect = pygame.Rect(
                card_padding,
                card_padding,
                WINDOW_WIDTH - card_padding * 2,
                WINDOW_HEIGHT - card_padding * 2
            )
            self._draw_rounded_rect(self.screen, card_color, card_rect, radius=25)
            
            # Draw title in turquoise
            title = font_title.render("Select Image to Annotate", True, turquoise)
            title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 130))
            self.screen.blit(title, title_rect)
            
            # Don't show directory info - cleaner look
            
            # Draw file list container
            list_start_y = 250
            list_height = WINDOW_HEIGHT - 400
            item_height = 60
            item_padding = 10
            
            # Draw files
            if not files:
                no_files = font_item.render("No image files found", True, (255, 100, 100))
                no_files_rect = no_files.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
                self.screen.blit(no_files, no_files_rect)
            else:
                visible_files = files[scroll_offset:scroll_offset + max_visible]
                hover_index = -1
                
                for i, filename in enumerate(visible_files):
                    actual_index = scroll_offset + i
                    y = list_start_y + i * (item_height + item_padding)
                    
                    # Item rectangle
                    item_rect = pygame.Rect(
                        card_padding + 40,
                        y,
                        WINDOW_WIDTH - (card_padding + 40) * 2,
                        item_height
                    )
                    
                    # Check hover
                    is_hovered = item_rect.collidepoint(mouse_pos)
                    if is_hovered:
                        hover_index = actual_index
                    
                    # Determine item color
                    if actual_index == selected_index:
                        item_bg_color = selected_color
                        text_color = (255, 255, 255)
                    elif is_hovered:
                        item_bg_color = item_hover
                        text_color = text_primary
                    else:
                        item_bg_color = item_color
                        text_color = text_secondary
                    
                    # Draw item background
                    self._draw_rounded_rect(self.screen, item_bg_color, item_rect, radius=12)
                    
                    # Draw file name
                    file_text = font_item.render(filename, True, text_color)
                    file_rect = file_text.get_rect(midleft=(item_rect.left + 20, item_rect.centery))
                    self.screen.blit(file_text, file_rect)
                
                # Draw scroll indicator if needed
                if len(files) > max_visible:
                    scroll_bar_height = 200
                    scroll_bar_y = list_start_y + (scroll_offset / len(files)) * scroll_bar_height
                    scroll_indicator = pygame.Rect(
                        WINDOW_WIDTH - card_padding - 20,
                        scroll_bar_y,
                        8,
                        40
                    )
                    self._draw_rounded_rect(self.screen, turquoise, scroll_indicator, radius=4)
            

            
            pygame.display.flip()
            self.clock.tick(60)
        
        return selected_file
    
    def _draw_rounded_rect(self, surface, color, rect, radius=20):
        """Draw a rounded rectangle."""
        pygame.draw.rect(surface, color, rect, border_radius=radius)
    
    def _draw_button(self, surface, text, x, y, width, height, color, hover_color, is_hovered, font):
        """Draw a modern button with hover effect."""
        button_rect = pygame.Rect(x, y, width, height)
        
        # Draw button with hover effect
        current_color = hover_color if is_hovered else color
        self._draw_rounded_rect(surface, current_color, button_rect, radius=15)
        
        # Draw text
        text_surface = font.render(text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=button_rect.center)
        surface.blit(text_surface, text_rect)
        
        return button_rect
    
    def _show_pygame_dialog(self, title, lines):
        """
        Show a modern yes/no dialog using Pygame.
        
        Args:
            title: Dialog title
            lines: List of text lines to display
            
        Returns:
            Boolean: True if user pressed Y, False if pressed N
        """
        # Light theme with turquoise accents
        bg_color = (245, 248, 250)  # Light blue-gray background
        card_color = (255, 255, 255)  # White card
        turquoise = (0, 128, 128)  # Dark turquoise
        turquoise_hover = (0, 160, 160)  # Lighter turquoise on hover
        cancel_color = (180, 190, 200)  # Light gray
        cancel_hover = (160, 170, 180)  # Darker gray on hover
        text_dark = (40, 50, 60)  # Dark text for body
        shadow_color = (200, 210, 220)  # Subtle shadow
        
        font_title = pygame.font.SysFont('Arial', 56, bold=True)
        font_body = pygame.font.SysFont('Arial', 32)
        font_button = pygame.font.SysFont('Arial', 36, bold=True)
        
        # Button states
        yes_hovered = False
        no_hovered = False
        
        # Button dimensions
        button_width = 200
        button_height = 60
        button_spacing = 40
        
        waiting = True
        response = False
        
        while waiting:
            mouse_pos = pygame.mouse.get_pos()
            
            # Check button hover states
            yes_button_rect = pygame.Rect(
                WINDOW_WIDTH // 2 - button_width - button_spacing // 2,
                WINDOW_HEIGHT - 150,
                button_width,
                button_height
            )
            no_button_rect = pygame.Rect(
                WINDOW_WIDTH // 2 + button_spacing // 2,
                WINDOW_HEIGHT - 150,
                button_width,
                button_height
            )
            
            yes_hovered = yes_button_rect.collidepoint(mouse_pos)
            no_hovered = no_button_rect.collidepoint(mouse_pos)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False
                    response = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_y:
                        waiting = False
                        response = True
                    elif event.key == pygame.K_n:
                        waiting = False
                        response = False
                    elif event.key == pygame.K_ESCAPE:
                        waiting = False
                        response = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if yes_hovered:
                        waiting = False
                        response = True
                    elif no_hovered:
                        waiting = False
                        response = False
            
            # Draw light background
            self.screen.fill(bg_color)
            
            # Draw card shadow (subtle)
            shadow_rect = pygame.Rect(
                WINDOW_WIDTH // 2 - 395,
                WINDOW_HEIGHT // 2 - 245,
                810,
                510
            )
            self._draw_rounded_rect(self.screen, shadow_color, shadow_rect, radius=30)
            
            # Draw card background
            card_rect = pygame.Rect(
                WINDOW_WIDTH // 2 - 400,
                WINDOW_HEIGHT // 2 - 250,
                800,
                500
            )
            self._draw_rounded_rect(self.screen, card_color, card_rect, radius=25)
            
            # Draw title in turquoise
            title_text = font_title.render(title, True, turquoise)
            title_rect = title_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 150))
            self.screen.blit(title_text, title_rect)
            
            # Draw message lines in dark text
            y_offset = WINDOW_HEIGHT // 2 - 60
            for line in lines:
                if line:
                    line_text = font_body.render(line, True, text_dark)
                    line_rect = line_text.get_rect(center=(WINDOW_WIDTH // 2, y_offset))
                    self.screen.blit(line_text, line_rect)
                y_offset += 45
            
            # Draw Yes button (turquoise)
            self._draw_button(
                self.screen,
                "Yes",
                yes_button_rect.x,
                yes_button_rect.y,
                button_width,
                button_height,
                turquoise,
                turquoise_hover,
                yes_hovered,
                font_button
            )
            
            # Draw No button (gray)
            self._draw_button(
                self.screen,
                "No",
                no_button_rect.x,
                no_button_rect.y,
                button_width,
                button_height,
                cancel_color,
                cancel_hover,
                no_hovered,
                font_button
            )
            
            # Draw hint
            hint_font = pygame.font.SysFont('Arial', 22)
            hint_text = hint_font.render("Click a button or press ESC to cancel", True, (100, 110, 120))
            hint_rect = hint_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 50))
            self.screen.blit(hint_text, hint_rect)
            
            pygame.display.flip()
            self.clock.tick(60)
        
        return response
    
    def _load_annotation_image(self, image_path):
        """
        Load and prepare an image for annotation.
        Image will be scaled to 1/4 screen size and positioned in top-right with padding.
        
        Args:
            image_path: Path to the image file
        """
        try:
            # Load image with pygame
            original_image = pygame.image.load(image_path)
            
            # Calculate target size (2/3 of screen for larger annotation area)
            target_width = int(WINDOW_WIDTH * 0.66)
            target_height = int(WINDOW_HEIGHT * 0.66)
            
            # Scale image maintaining aspect ratio
            original_rect = original_image.get_rect()
            scale_factor = min(target_width / original_rect.width, 
                             target_height / original_rect.height)
            
            new_width = int(original_rect.width * scale_factor)
            new_height = int(original_rect.height * scale_factor)
            
            self.annotation_image = pygame.transform.scale(original_image, (new_width, new_height))
            
            # Position in top-left with padding
            padding = 40
            x = padding
            y = padding
            
            self.annotation_rect = pygame.Rect(x, y, new_width, new_height)
            
            print(f"Loaded annotation image: {os.path.basename(image_path)}")
            print(f"Image size: {new_width}x{new_height} at position ({x}, {y})")
            
        except Exception as e:
            print(f"Error loading image: {e}")
            self.annotation_image = None
            self.annotation_rect = None
    
    def handle_events(self):
        """Process Pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Check if record button was clicked
                mouse_pos = pygame.mouse.get_pos()
                if self.ui_manager.is_button_clicked(mouse_pos):
                    # Toggle recording
                    if self.recording_manager.is_recording:
                        # Stop recording
                        output_path = self.recording_manager.stop_recording()
                        if output_path:
                            print(f"Recording saved: {output_path}")
                    else:
                        # Start recording
                        success = self.recording_manager.start_recording(
                            WINDOW_WIDTH, 
                            WINDOW_HEIGHT, 
                            FPS
                        )
                        if success:
                            print("Recording started")
                        else:
                            print("Failed to start recording")
        return True
    
    def update(self):
        """Update application state."""
        # Read camera frame with error handling
        success, frame = self.cap.read()
        if not success or frame is None:
            print("Warning: Failed to read camera frame")
            # Return None to indicate frame read failure
            return None, None
        
        # Process frame with GestureController
        # Note: HandTracker already flips the frame internally for mirror effect
        try:
            annotated_frame, gesture_events = self.gesture_controller.process_frame(frame)
        except Exception as e:
            print(f"Error processing frame: {e}")
            return frame, {}
        
        # Get hand state from gesture controller (already processed)
        hand_state = self.gesture_controller.current_hand_state
        
        # Handle tracking loss: if hand is not present, terminate stroke and deactivate pen
        if hand_state is not None and not hand_state.is_present:
            # Tracking lost - terminate current stroke
            if self.prev_pen_position is not None:
                self.prev_pen_position = None
                self.smoothed_position = None
        
        # Handle rock sign gesture → clear canvas action
        if gesture_events['rock_sign_pressed']:
            self.drawing_manager.clear_canvas()
            self.prev_pen_position = None  # Reset pen position tracking
            print("Canvas cleared")
        
        # Handle thumbs up gesture → cycle color action
        if gesture_events['thumbs_up_pressed']:
            new_color = self.drawing_manager.cycle_color()
            print(f"Color changed to: {new_color}")
        
        # Handle drawing logic
        if self.gesture_controller.is_pen_active():
            # Get current pen position
            raw_pen_position = self.gesture_controller.get_pen_position(hand_state)
            
            if raw_pen_position is not None:
                # Apply smoothing to reduce shakiness
                if self.smoothed_position is None:
                    # First position: no smoothing needed
                    self.smoothed_position = raw_pen_position
                else:
                    # Exponential moving average smoothing
                    # smoothed = smoothed * factor + raw * (1 - factor)
                    smoothed_x = self.smoothed_position[0] * self.smoothing_factor + raw_pen_position[0] * (1 - self.smoothing_factor)
                    smoothed_y = self.smoothed_position[1] * self.smoothing_factor + raw_pen_position[1] * (1 - self.smoothing_factor)
                    self.smoothed_position = (int(smoothed_x), int(smoothed_y))
                
                # Use smoothed position for drawing
                current_pen_position = self.smoothed_position
                
                # Check if this is pen activation (start new stroke) or continuation
                if self.prev_pen_position is not None:
                    # Continuation: connect to previous position
                    self.drawing_manager.draw_stroke(
                        self.prev_pen_position,
                        current_pen_position
                    )
                else:
                    # Pen activation: draw a small dot at the starting position
                    # (draw a line from current position to itself)
                    self.drawing_manager.draw_stroke(
                        current_pen_position,
                        current_pen_position
                    )
                
                # Update previous position for next frame
                self.prev_pen_position = current_pen_position
        else:
            # Pen is inactive: terminate stroke by resetting previous position
            self.prev_pen_position = None
            self.smoothed_position = None  # Reset smoothing when pen is inactive
        
        return annotated_frame, gesture_events
    
    def render(self, frame, gesture_events):
        """Render all layers to screen."""
        if frame is None:
            return
        
        # Convert OpenCV frame (BGR) to Pygame surface (RGB)
        # Frame is already flipped in update() method
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Resize frame to window size if needed
        if frame_rgb.shape[1] != WINDOW_WIDTH or frame_rgb.shape[0] != WINDOW_HEIGHT:
            frame_rgb = cv2.resize(frame_rgb, (WINDOW_WIDTH, WINDOW_HEIGHT))
        
        # Create Pygame surface from frame
        frame_surface = pygame.surfarray.make_surface(frame_rgb.swapaxes(0, 1))
        
        # Draw webcam feed as background
        self.screen.blit(frame_surface, (0, 0))
        
        # Draw annotation image if loaded
        if self.annotation_image is not None and self.annotation_rect is not None:
            self.screen.blit(self.annotation_image, self.annotation_rect)
        
        # Draw the drawing layer (now fully opaque since no hand landmarks visible)
        drawing_surface = self.drawing_manager.get_drawing_surface()
        self.screen.blit(drawing_surface, (0, 0))
        
        # Draw cursor dot at index finger position (on top of everything)
        hand_state = self.gesture_controller.current_hand_state
        if hand_state and hand_state.is_present:
            pen_pos = self.gesture_controller.get_pen_position(hand_state)
            if pen_pos:
                # Use current pen color for cursor
                cursor_color = self.drawing_manager.get_current_color()
                cursor_radius = 8
                pygame.draw.circle(self.screen, cursor_color, pen_pos, cursor_radius)
                # Add white outline for visibility
                pygame.draw.circle(self.screen, (255, 255, 255), pen_pos, cursor_radius, 2)
        
        # Draw UI elements
        self.ui_manager.draw_record_button(self.screen)
        
        # Show/hide vinyl indicator based on recording state
        if self.recording_manager.is_recording:
            # Update vinyl rotation during recording
            self.ui_manager.update_vinyl_rotation()
            # Draw vinyl indicator
            self.ui_manager.draw_vinyl_indicator(self.screen)
        
        # Update display
        pygame.display.flip()
        
        # Capture composited frame if recording is active
        if self.recording_manager.is_recording:
            # Capture the composited frame (webcam + drawing layer + UI)
            self.recording_manager.capture_frame(self.screen)
    
    def run(self):
        """Main application loop."""
        # Show launch screen first
        if not self._show_launch_screen():
            # User closed window or pressed ESC on launch screen
            pygame.quit()
            return
        
        # Initialize camera and components after user clicks start
        self._initialize_camera_and_components()
        
        running = True
        
        print("Holo-Board running. Press ESC to exit.")
        print("Gestures: Point to draw, Open hand to stop, Rock sign to clear, Thumbs up to change color")
        
        consecutive_frame_failures = 0
        max_consecutive_failures = 30  # Allow 30 consecutive failures before giving up
        
        while running:
            try:
                # Handle events
                running = self.handle_events()
                
                # Update state
                frame, gesture_events = self.update()
                
                # Check for frame read failures
                if frame is None:
                    consecutive_frame_failures += 1
                    if consecutive_frame_failures >= max_consecutive_failures:
                        print(f"Error: Camera stopped responding after {max_consecutive_failures} consecutive failures")
                        print("Exiting application...")
                        running = False
                        break
                    continue
                else:
                    # Reset failure counter on successful frame read
                    consecutive_frame_failures = 0
                
                # Render
                self.render(frame, gesture_events)
                
                # Maintain frame rate
                self.clock.tick(FPS)
                
            except KeyboardInterrupt:
                print("\nInterrupted by user")
                running = False
            except Exception as e:
                print(f"Error in main loop: {e}")
                import traceback
                traceback.print_exc()
                # Continue running unless it's a critical error
                consecutive_frame_failures += 1
                if consecutive_frame_failures >= max_consecutive_failures:
                    print("Too many errors, exiting...")
                    running = False
        
        # Cleanup
        self.cleanup()
    
    def cleanup(self):
        """Clean up resources."""
        print("Shutting down Holo-Board...")
        
        try:
            if self.cap is not None:
                self.cap.release()
        except Exception as e:
            print(f"Error releasing camera: {e}")
        
        try:
            self.gesture_controller.close()
        except Exception as e:
            print(f"Error closing gesture controller: {e}")
        
        try:
            self.recording_manager.cleanup()
        except Exception as e:
            print(f"Error cleaning up recording manager: {e}")
        
        try:
            pygame.quit()
        except Exception as e:
            print(f"Error quitting pygame: {e}")


def main():
    """Entry point for Holo-Board application."""
    try:
        app = HoloBoardApp()
        app.run()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
