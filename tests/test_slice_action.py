#!/usr/bin/env python3
"""
Unit tests for slice action and Effect class
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
from main import Effect


class TestEffect(unittest.TestCase):
    """Test cases for Effect class"""
    
    def setUp(self):
        """Set up test fixtures"""
        pygame.init()
        self.dummy_image = pygame.Surface((50, 50))
    
    def test_effect_creation(self):
        """Test that an effect can be created with all required fields"""
        effect = Effect(
            x=100.0,
            y=200.0,
            image=self.dummy_image,
            duration=0.5,
            elapsed=0.0
        )
        
        self.assertEqual(effect.x, 100.0)
        self.assertEqual(effect.y, 200.0)
        self.assertEqual(effect.duration, 0.5)
        self.assertEqual(effect.elapsed, 0.0)
    
    def test_effect_update_returns_true_when_active(self):
        """Test that effect.update returns True when still active"""
        effect = Effect(
            x=100.0,
            y=200.0,
            image=self.dummy_image,
            duration=0.5,
            elapsed=0.0
        )
        
        # Update with small delta time
        is_active = effect.update(0.1)
        
        self.assertTrue(is_active)
        self.assertEqual(effect.elapsed, 0.1)
    
    def test_effect_update_returns_false_when_expired(self):
        """Test that effect.update returns False when expired"""
        effect = Effect(
            x=100.0,
            y=200.0,
            image=self.dummy_image,
            duration=0.5,
            elapsed=0.0
        )
        
        # Update with time that exceeds duration
        is_active = effect.update(0.6)
        
        self.assertFalse(is_active)
        self.assertEqual(effect.elapsed, 0.6)
    
    def test_effect_update_accumulates_time(self):
        """Test that effect.update accumulates elapsed time"""
        effect = Effect(
            x=100.0,
            y=200.0,
            image=self.dummy_image,
            duration=0.5,
            elapsed=0.0
        )
        
        # Update multiple times
        effect.update(0.1)
        effect.update(0.1)
        effect.update(0.1)
        
        self.assertAlmostEqual(effect.elapsed, 0.3, places=5)


if __name__ == '__main__':
    unittest.main()
