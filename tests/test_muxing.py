#!/usr/bin/env python3
"""
Test for audio/video muxing functionality.
"""

import os
import sys
import pytest
import pygame
import cv2
import time
import wave
import struct

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Import after path setup
sys.path.insert(0, os.path.join(PROJECT_ROOT, 'my_apps', 'Holo-Board'))
from main import RecordingManager


class TestAudioVideoMuxing:
    """Test suite for audio/video muxing functionality."""
    
    @pytest.fixture
    def recording_manager(self):
        """Create a RecordingManager instance for testing."""
        return RecordingManager()
    
    @pytest.fixture
    def test_surface(self):
        """Create a test Pygame surface."""
        pygame.init()
        surface = pygame.Surface((640, 480))
        surface.fill((0, 255, 0))  # Green background
        yield surface
        pygame.quit()
    
    def create_test_audio_file(self, filename, duration=1.0):
        """
        Create a test WAV audio file with a simple tone.
        
        Args:
            filename: Path to save the WAV file
            duration: Duration in seconds
        """
        sample_rate = 44100
        frequency = 440  # A4 note
        num_samples = int(sample_rate * duration)
        
        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(1)  # Mono
            wf.setsampwidth(2)  # 16-bit
            wf.setframerate(sample_rate)
            
            # Generate sine wave
            for i in range(num_samples):
                value = int(32767 * 0.3 * (i % (sample_rate // frequency)) / (sample_rate // frequency))
                wf.writeframes(struct.pack('<h', value))
    
    def create_test_video_file(self, filename, width=640, height=480, fps=30, duration=1.0):
        """
        Create a test video file.
        
        Args:
            filename: Path to save the video file
            width: Video width
            height: Video height
            fps: Frames per second
            duration: Duration in seconds
        """
        import numpy as np
        
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        writer = cv2.VideoWriter(filename, fourcc, fps, (width, height))
        
        num_frames = int(fps * duration)
        for i in range(num_frames):
            # Create a frame with changing color (numpy array)
            b = i * 255 // num_frames
            g = 128
            r = 255 - (i * 255 // num_frames)
            
            # Create BGR image
            img = np.zeros((height, width, 3), dtype=np.uint8)
            img[:, :] = [b, g, r]
            
            writer.write(img)
        
        writer.release()
    
    def test_mux_audio_video_success(self, recording_manager):
        """Test successful audio/video muxing."""
        # Create temporary test files
        test_video = "test_video_temp.mp4"
        test_audio = "test_audio_temp.wav"
        output_file = "test_output_muxed.mp4"
        
        try:
            # Create test files
            self.create_test_video_file(test_video)
            self.create_test_audio_file(test_audio)
            
            # Perform muxing
            success = recording_manager.mux_audio_video(test_video, test_audio, output_file)
            
            # Verify muxing succeeded
            assert success == True
            assert os.path.exists(output_file)
            assert os.path.getsize(output_file) > 0
            
            # Verify output file is a valid video with audio
            cap = cv2.VideoCapture(output_file)
            assert cap.isOpened()
            
            # Read a frame to verify video content
            success_read, frame = cap.read()
            assert success_read == True
            assert frame is not None
            
            cap.release()
            
        finally:
            # Cleanup
            for f in [test_video, test_audio, output_file]:
                if os.path.exists(f):
                    os.remove(f)
    
    def test_mux_audio_video_missing_video(self, recording_manager):
        """Test muxing with missing video file."""
        test_audio = "test_audio_temp.wav"
        output_file = "test_output_muxed.mp4"
        
        try:
            # Create only audio file
            self.create_test_audio_file(test_audio)
            
            # Attempt muxing with non-existent video
            success = recording_manager.mux_audio_video("nonexistent.mp4", test_audio, output_file)
            
            # Muxing should fail
            assert success == False
            
        finally:
            # Cleanup
            for f in [test_audio, output_file]:
                if os.path.exists(f):
                    os.remove(f)
    
    def test_mux_audio_video_missing_audio(self, recording_manager):
        """Test muxing with missing audio file."""
        test_video = "test_video_temp.mp4"
        output_file = "test_output_muxed.mp4"
        
        try:
            # Create only video file
            self.create_test_video_file(test_video)
            
            # Attempt muxing with non-existent audio
            success = recording_manager.mux_audio_video(test_video, "nonexistent.wav", output_file)
            
            # Muxing should fail
            assert success == False
            
        finally:
            # Cleanup
            for f in [test_video, output_file]:
                if os.path.exists(f):
                    os.remove(f)
    
    def test_stop_recording_with_muxing(self, recording_manager, test_surface):
        """Test that stop_recording properly muxes audio and video."""
        # This test requires PyAudio to be available
        if not recording_manager.audio_available:
            pytest.skip("PyAudio not available")
        
        try:
            # Start recording
            recording_manager.start_recording(640, 480, 30)
            
            # Capture some frames
            for _ in range(30):  # 1 second at 30 FPS
                recording_manager.capture_frame(test_surface)
                time.sleep(0.033)  # ~30 FPS
            
            # Stop recording (should trigger muxing)
            output_path = recording_manager.stop_recording()
            
            # Verify output file exists
            assert output_path is not None
            assert os.path.exists(output_path)
            assert os.path.getsize(output_path) > 0
            
            # Verify it's a valid video file
            cap = cv2.VideoCapture(output_path)
            assert cap.isOpened()
            cap.release()
            
        finally:
            # Cleanup
            if output_path and os.path.exists(output_path):
                os.remove(output_path)
    
    def test_stop_recording_without_audio(self, recording_manager, test_surface):
        """Test that stop_recording works without audio (video-only)."""
        try:
            # Start recording
            recording_manager.start_recording(640, 480, 30)
            
            # Manually disable audio to simulate no audio capture
            if recording_manager.audio_stream:
                recording_manager.audio_stream.stop_stream()
                recording_manager.audio_stream.close()
                recording_manager.audio_stream = None
            if recording_manager.audio_thread:
                recording_manager.audio_stop_event.set()
                recording_manager.audio_thread.join(timeout=1.0)
                recording_manager.audio_thread = None
            
            # Capture some frames
            for _ in range(10):
                recording_manager.capture_frame(test_surface)
            
            # Stop recording (should save video-only)
            output_path = recording_manager.stop_recording()
            
            # Verify output file exists
            assert output_path is not None
            assert os.path.exists(output_path)
            assert os.path.getsize(output_path) > 0
            
        finally:
            # Cleanup
            if output_path and os.path.exists(output_path):
                os.remove(output_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
