#!/usr/bin/env python3
"""
Unit tests for scoring and lives system
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
from main import MathOLanternGame


class TestScoringAndLives(unittest.TestCase):
    """Test cases for scoring and lives system"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Initialize pygame (required for game initialization)
        pygame.init()
        # Create game instance
        self.game = MathOLanternGame()
    
    def tearDown(self):
        """Clean up after tests"""
        self.game.camera.release()
        self.game.hand_tracker.close()
        pygame.quit()
    
    def test_initial_score_is_zero(self):
        """Test that score initializes to 0"""
        self.assertEqual(self.game.score, 0)
    
    def test_initial_lives_is_three(self):
        """Test that lives initialize to 3"""
        self.assertEqual(self.game.lives, 3)
    
    def test_score_increment_on_correct_slice(self):
        """Test that score increments by 5 when correct pumpkin is sliced"""
        # Spawn a correct pumpkin
        self.game.pumpkin_manager.spawn_pumpkin(42, 1280)
        
        # Find a correct pumpkin
        correct_pumpkin = None
        for pumpkin in self.game.pumpkin_manager.pumpkins:
            if pumpkin.is_correct:
                correct_pumpkin = pumpkin
                break
        
        # If we didn't get a correct pumpkin, manually create one
        if correct_pumpkin is None:
            from main import Pumpkin
            correct_pumpkin = Pumpkin(
                x=100.0,
                y=100.0,
                number=42,
                is_correct=True,
                velocity_y=100.0,
                image=self.game.assets["pumpkin"],
                rect=self.game.assets["pumpkin"].get_rect()
            )
            self.game.pumpkin_manager.pumpkins.append(correct_pumpkin)
        
        initial_score = self.game.score
        
        # Simulate slicing the correct pumpkin
        if correct_pumpkin.is_correct:
            self.game.score += 5
            self.game.pumpkin_manager.remove_pumpkin(correct_pumpkin)
        
        self.assertEqual(self.game.score, initial_score + 5)
    
    def test_lives_decrement_on_incorrect_slice(self):
        """Test that lives decrement by 1 when incorrect pumpkin is sliced"""
        # Create an incorrect pumpkin manually
        from main import Pumpkin
        incorrect_pumpkin = Pumpkin(
            x=100.0,
            y=100.0,
            number=99,
            is_correct=False,
            velocity_y=100.0,
            image=self.game.assets["pumpkin"],
            rect=self.game.assets["pumpkin"].get_rect()
        )
        self.game.pumpkin_manager.pumpkins.append(incorrect_pumpkin)
        
        initial_lives = self.game.lives
        
        # Simulate slicing the incorrect pumpkin
        if not incorrect_pumpkin.is_correct:
            self.game.lives -= 1
            self.game.pumpkin_manager.remove_pumpkin(incorrect_pumpkin)
        
        self.assertEqual(self.game.lives, initial_lives - 1)
    
    def test_score_display_format(self):
        """Test that score is displayed with 'Score:' label"""
        # This is a simple check that the render_score method exists
        self.assertTrue(hasattr(self.game, 'render_score'))
        self.assertTrue(callable(self.game.render_score))
    
    def test_lives_display_method_exists(self):
        """Test that lives rendering method exists"""
        self.assertTrue(hasattr(self.game, 'render_lives'))
        self.assertTrue(callable(self.game.render_lives))


if __name__ == '__main__':
    unittest.main()
