#!/usr/bin/env python3
"""
Unit tests for RecordingManager class.
Tests video recording functionality (video only, no audio yet).
"""

import os
import sys
import pytest
import pygame
import cv2
import time

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Import after path setup
sys.path.insert(0, os.path.join(PROJECT_ROOT, 'my_apps', 'Holo-Board'))
from main import RecordingManager


class TestRecordingManager:
    """Test suite for RecordingManager."""
    
    @pytest.fixture
    def recording_manager(self):
        """Create a RecordingManager instance for testing."""
        return RecordingManager()
    
    @pytest.fixture
    def test_surface(self):
        """Create a test Pygame surface."""
        pygame.init()
        surface = pygame.Surface((640, 480))
        surface.fill((255, 0, 0))  # Red background
        yield surface
        pygame.quit()
    
    def test_initial_state(self, recording_manager):
        """Test that RecordingManager initializes with correct state."""
        assert recording_manager.is_recording == False
        assert recording_manager.video_writer is None
        assert recording_manager.output_filename is None
        assert recording_manager.frame_count == 0
        assert recording_manager.start_time is None
        
        # Audio state
        assert recording_manager.audio_stream is None
        assert recording_manager.audio_thread is None
        assert recording_manager.temp_audio_filename is None
    
    def test_generate_filename(self, recording_manager):
        """Test filename generation with timestamp pattern."""
        full_path = recording_manager.generate_filename()
        
        # Extract just the filename from the full path
        import os
        filename = os.path.basename(full_path)
        
        # Check format: holo-board-recording-YYYYMMDD-HHMMSS.mp4
        assert filename.startswith("holo-board-recording-")
        assert filename.endswith(".mp4")
        
        # Extract timestamp part
        timestamp_part = filename.replace("holo-board-recording-", "").replace(".mp4", "")
        date_part, time_part = timestamp_part.split("-")
        
        # Verify date format (YYYYMMDD)
        assert len(date_part) == 8
        assert date_part.isdigit()
        
        # Verify time format (HHMMSS)
        assert len(time_part) == 6
        assert time_part.isdigit()
    
    def test_generate_unique_filenames(self, recording_manager):
        """Test that multiple recordings generate unique filenames."""
        filename1 = recording_manager.generate_filename()
        time.sleep(1.1)  # Wait to ensure different timestamp
        filename2 = recording_manager.generate_filename()
        
        assert filename1 != filename2
    
    def test_start_recording(self, recording_manager):
        """Test starting a recording session."""
        success = recording_manager.start_recording(640, 480, 30)
        
        assert success == True
        assert recording_manager.is_recording == True
        assert recording_manager.video_writer is not None
        assert recording_manager.output_filename is not None
        assert recording_manager.frame_count == 0
        assert recording_manager.start_time is not None
        
        # Cleanup
        recording_manager.stop_recording()
        if os.path.exists(recording_manager.output_filename or ""):
            os.remove(recording_manager.output_filename)
    
    def test_start_recording_when_already_recording(self, recording_manager):
        """Test that starting recording when already recording returns False."""
        recording_manager.start_recording(640, 480, 30)
        
        # Try to start again
        success = recording_manager.start_recording(640, 480, 30)
        assert success == False
        
        # Cleanup
        filename = recording_manager.output_filename
        recording_manager.stop_recording()
        if os.path.exists(filename):
            os.remove(filename)
    
    def test_capture_frame(self, recording_manager, test_surface):
        """Test capturing a frame to video."""
        recording_manager.start_recording(640, 480, 30)
        
        # Capture a frame
        success = recording_manager.capture_frame(test_surface)
        assert success == True
        assert recording_manager.frame_count == 1
        
        # Capture another frame
        success = recording_manager.capture_frame(test_surface)
        assert success == True
        assert recording_manager.frame_count == 2
        
        # Cleanup
        filename = recording_manager.output_filename
        recording_manager.stop_recording()
        if os.path.exists(filename):
            os.remove(filename)
    
    def test_capture_frame_when_not_recording(self, recording_manager, test_surface):
        """Test that capturing frame when not recording returns False."""
        success = recording_manager.capture_frame(test_surface)
        assert success == False
    
    def test_stop_recording(self, recording_manager, test_surface):
        """Test stopping a recording session."""
        recording_manager.start_recording(640, 480, 30)
        
        # Capture some frames
        for _ in range(5):
            recording_manager.capture_frame(test_surface)
        
        # Stop recording
        output_path = recording_manager.stop_recording()
        
        assert output_path is not None
        assert os.path.exists(output_path)
        assert recording_manager.is_recording == False
        assert recording_manager.video_writer is None
        assert recording_manager.frame_count == 0
        assert recording_manager.start_time is None
        
        # Cleanup
        if os.path.exists(output_path):
            os.remove(output_path)
    
    def test_stop_recording_when_not_recording(self, recording_manager):
        """Test that stopping recording when not recording returns None."""
        output_path = recording_manager.stop_recording()
        assert output_path is None
    
    def test_get_recording_state(self, recording_manager):
        """Test getting recording state information."""
        # Initial state
        state = recording_manager.get_recording_state()
        assert state['is_recording'] == False
        assert state['frame_count'] == 0
        assert state['duration'] == 0.0
        assert state['output_path'] is None
        
        # During recording
        recording_manager.start_recording(640, 480, 30)
        state = recording_manager.get_recording_state()
        assert state['is_recording'] == True
        assert state['frame_count'] == 0
        assert state['output_path'] is not None
        
        # Cleanup
        filename = recording_manager.output_filename
        recording_manager.stop_recording()
        if os.path.exists(filename):
            os.remove(filename)
    
    def test_output_file_creation(self, recording_manager, test_surface):
        """Test that output file is created and contains video data."""
        recording_manager.start_recording(640, 480, 30)
        
        # Capture multiple frames
        for _ in range(10):
            recording_manager.capture_frame(test_surface)
        
        output_path = recording_manager.stop_recording()
        
        # Verify file exists and has content
        assert os.path.exists(output_path)
        assert os.path.getsize(output_path) > 0
        
        # Try to open with OpenCV to verify it's a valid video
        cap = cv2.VideoCapture(output_path)
        assert cap.isOpened()
        
        # Read a frame to verify video content
        success, frame = cap.read()
        assert success == True
        assert frame is not None
        
        cap.release()
        
        # Cleanup
        if os.path.exists(output_path):
            os.remove(output_path)


    def test_audio_initialization(self, recording_manager):
        """Test that audio capture is initialized when available."""
        # Check if PyAudio is available
        if not recording_manager.audio_available:
            pytest.skip("PyAudio not available")
        
        # Start recording
        recording_manager.start_recording(640, 480, 30)
        
        # Check audio state
        assert recording_manager.audio_stream is not None
        assert recording_manager.audio_thread is not None
        assert recording_manager.audio_thread.is_alive()
        
        # Cleanup
        filename = recording_manager.output_filename
        recording_manager.stop_recording()
        if os.path.exists(filename):
            os.remove(filename)
        # Clean up audio file if created
        if recording_manager.temp_audio_filename and os.path.exists(recording_manager.temp_audio_filename):
            os.remove(recording_manager.temp_audio_filename)
    
    def test_audio_capture_graceful_failure(self, recording_manager):
        """Test that recording continues with video-only if audio fails."""
        # Start recording (should work even if audio fails)
        success = recording_manager.start_recording(640, 480, 30)
        
        # Recording should start successfully regardless of audio availability
        assert success == True
        assert recording_manager.is_recording == True
        
        # Cleanup
        filename = recording_manager.output_filename
        recording_manager.stop_recording()
        if os.path.exists(filename):
            os.remove(filename)
        # Clean up audio file if created
        if recording_manager.temp_audio_filename and os.path.exists(recording_manager.temp_audio_filename):
            os.remove(recording_manager.temp_audio_filename)
    
    def test_audio_file_creation(self, recording_manager, test_surface):
        """Test that audio file is created when audio is available."""
        # Check if PyAudio is available
        if not recording_manager.audio_available:
            pytest.skip("PyAudio not available")
        
        # Start recording
        recording_manager.start_recording(640, 480, 30)
        
        # Capture some frames and let audio capture run
        for _ in range(30):  # 1 second at 30 FPS
            recording_manager.capture_frame(test_surface)
            time.sleep(0.033)  # ~30 FPS
        
        # Stop recording
        output_path = recording_manager.stop_recording()
        
        # Check that audio file was created
        if recording_manager.temp_audio_filename:
            assert os.path.exists(recording_manager.temp_audio_filename)
            assert os.path.getsize(recording_manager.temp_audio_filename) > 0
        
        # Cleanup
        if os.path.exists(output_path):
            os.remove(output_path)
        if recording_manager.temp_audio_filename and os.path.exists(recording_manager.temp_audio_filename):
            os.remove(recording_manager.temp_audio_filename)
    
    def test_cleanup(self, recording_manager):
        """Test that cleanup properly releases resources."""
        # Start recording
        recording_manager.start_recording(640, 480, 30)
        filename = recording_manager.output_filename
        
        # Call cleanup
        recording_manager.cleanup()
        
        # Check that recording was stopped
        assert recording_manager.is_recording == False
        assert recording_manager.pyaudio_instance is None
        
        # Cleanup files
        if os.path.exists(filename):
            os.remove(filename)
        if recording_manager.temp_audio_filename and os.path.exists(recording_manager.temp_audio_filename):
            os.remove(recording_manager.temp_audio_filename)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
