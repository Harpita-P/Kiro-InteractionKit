#!/usr/bin/env python3
"""
Unit tests for Pumpkin and PumpkinManager classes
"""

import os
import sys
import unittest
import pygame

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Import after path setup
sys.path.insert(0, os.path.join(PROJECT_ROOT, 'my_apps', 'Math-O-Lantern'))
from main import Pumpkin, PumpkinManager


class TestPumpkin(unittest.TestCase):
    """Test cases for Pumpkin class"""
    
    def setUp(self):
        """Set up test fixtures"""
        pygame.init()
        # Create a dummy surface for testing
        self.dummy_image = pygame.Surface((50, 50))
        self.dummy_rect = self.dummy_image.get_rect()
    
    def test_pumpkin_creation(self):
        """Test that a pumpkin can be created with all required fields"""
        pumpkin = Pumpkin(
            x=100.0,
            y=50.0,
            number=42,
            is_correct=True,
            velocity_y=100.0,
            image=self.dummy_image,
            rect=self.dummy_rect
        )
        
        self.assertEqual(pumpkin.x, 100.0)
        self.assertEqual(pumpkin.y, 50.0)
        self.assertEqual(pumpkin.number, 42)
        self.assertTrue(pumpkin.is_correct)
        self.assertEqual(pumpkin.velocity_y, 100.0)
    
    def test_pumpkin_update_moves_downward(self):
        """Test that pumpkin moves downward when updated"""
        pumpkin = Pumpkin(
            x=100.0,
            y=50.0,
            number=42,
            is_correct=True,
            velocity_y=100.0,
            image=self.dummy_image,
            rect=self.dummy_rect.copy()
        )
        
        initial_y = pumpkin.y
        pumpkin.update(1.0)  # 1 second
        
        # Pumpkin should move down by velocity_y * delta_time
        self.assertEqual(pumpkin.y, initial_y + 100.0)
        self.assertEqual(pumpkin.rect.y, int(initial_y + 100.0))
    
    def test_pumpkin_is_off_screen(self):
        """Test off-screen detection"""
        pumpkin = Pumpkin(
            x=100.0,
            y=721.0,
            number=42,
            is_correct=True,
            velocity_y=100.0,
            image=self.dummy_image,
            rect=self.dummy_rect
        )
        
        # Pumpkin at y=721 should be off screen for 720px height
        self.assertTrue(pumpkin.is_off_screen(720))
        
        # Pumpkin at y=500 should not be off screen for 720px height
        pumpkin.y = 500.0
        self.assertFalse(pumpkin.is_off_screen(720))


class TestPumpkinManager(unittest.TestCase):
    """Test cases for PumpkinManager class"""
    
    def setUp(self):
        """Set up test fixtures"""
        pygame.init()
        self.dummy_image = pygame.Surface((50, 50))
        self.manager = PumpkinManager(self.dummy_image)
    
    def test_manager_initialization(self):
        """Test that manager initializes with empty pumpkin list"""
        self.assertEqual(len(self.manager.pumpkins), 0)
        self.assertEqual(self.manager.spawn_timer, 0.0)
        self.assertEqual(self.manager.spawn_interval, 1.2)  # Updated for better gameplay
    
    def test_spawn_pumpkin_creates_pumpkin(self):
        """Test that spawn_pumpkin creates a pumpkin"""
        initial_count = len(self.manager.pumpkins)
        self.manager.spawn_pumpkin(correct_answer=42, screen_width=1280)
        
        self.assertEqual(len(self.manager.pumpkins), initial_count + 1)
        
        pumpkin = self.manager.pumpkins[0]
        self.assertIsNotNone(pumpkin.number)
        self.assertIsInstance(pumpkin.is_correct, bool)
        self.assertTrue(pumpkin.velocity_y > 0)  # Should be moving downward
    
    def test_spawn_pumpkin_correct_answer_distribution(self):
        """Test that approximately 60% of pumpkins have correct answer"""
        correct_answer = 42
        spawn_count = 100
        
        for _ in range(spawn_count):
            self.manager.spawn_pumpkin(correct_answer, screen_width=1280)
        
        correct_count = sum(1 for p in self.manager.pumpkins if p.is_correct)
        correct_percentage = correct_count / spawn_count
        
        # Should be approximately 60% (allow ±15% variance for randomness)
        self.assertGreater(correct_percentage, 0.45)
        self.assertLess(correct_percentage, 0.75)
    
    def test_spawn_pumpkin_assigns_numbers(self):
        """Test that spawned pumpkins have assigned numbers"""
        self.manager.spawn_pumpkin(correct_answer=42, screen_width=1280)
        
        pumpkin = self.manager.pumpkins[0]
        self.assertIsNotNone(pumpkin.number)
        self.assertIsInstance(pumpkin.number, int)
    
    def test_update_moves_pumpkins(self):
        """Test that update moves pumpkins downward"""
        self.manager.spawn_pumpkin(correct_answer=42, screen_width=1280)
        pumpkin = self.manager.pumpkins[0]
        
        initial_y = pumpkin.y
        self.manager.update(delta_time=1.0, screen_height=720)
        
        # Pumpkin should have moved down
        self.assertGreater(pumpkin.y, initial_y)
    
    def test_update_removes_off_screen_pumpkins(self):
        """Test that off-screen pumpkins are removed"""
        self.manager.spawn_pumpkin(correct_answer=42, screen_width=1280)
        pumpkin = self.manager.pumpkins[0]
        
        # Move pumpkin way off screen
        pumpkin.y = 1000.0
        
        self.manager.update(delta_time=0.1, screen_height=720)
        
        # Pumpkin should be removed
        self.assertEqual(len(self.manager.pumpkins), 0)
    
    def test_remove_pumpkin(self):
        """Test that remove_pumpkin removes specified pumpkin"""
        self.manager.spawn_pumpkin(correct_answer=42, screen_width=1280)
        pumpkin = self.manager.pumpkins[0]
        
        self.manager.remove_pumpkin(pumpkin)
        
        self.assertEqual(len(self.manager.pumpkins), 0)
    
    def test_clear_all(self):
        """Test that clear_all removes all pumpkins"""
        # Spawn multiple pumpkins
        for _ in range(5):
            self.manager.spawn_pumpkin(correct_answer=42, screen_width=1280)
        
        self.assertEqual(len(self.manager.pumpkins), 5)
        
        self.manager.clear_all()
        
        self.assertEqual(len(self.manager.pumpkins), 0)
    
    def test_check_collision_detects_overlap(self):
        """Test that check_collision detects cursor-pumpkin overlap"""
        self.manager.spawn_pumpkin(correct_answer=42, screen_width=1280)
        pumpkin = self.manager.pumpkins[0]
        
        # Set pumpkin to known position
        pumpkin.x = 100.0
        pumpkin.y = 100.0
        pumpkin.rect.x = 100
        pumpkin.rect.y = 100
        
        # Cursor overlapping pumpkin
        result = self.manager.check_collision(cursor_x=110.0, cursor_y=110.0)
        self.assertIsNotNone(result)
        self.assertEqual(result, pumpkin)
    
    def test_check_collision_no_overlap(self):
        """Test that check_collision returns None when no overlap"""
        self.manager.spawn_pumpkin(correct_answer=42, screen_width=1280)
        pumpkin = self.manager.pumpkins[0]
        
        # Set pumpkin to known position
        pumpkin.x = 100.0
        pumpkin.y = 100.0
        pumpkin.rect.x = 100
        pumpkin.rect.y = 100
        
        # Cursor far from pumpkin
        result = self.manager.check_collision(cursor_x=500.0, cursor_y=500.0)
        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()
