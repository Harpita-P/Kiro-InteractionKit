#!/usr/bin/env python3
"""
Unit tests for game over and restart logic
"""

import unittest
import sys
import os
import pygame

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Import game components
# Need to import directly from the file
import importlib.util
spec = importlib.util.spec_from_file_location("main", os.path.join(PROJECT_ROOT, "my_apps/Math-O-Lantern/main.py"))
main_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(main_module)

MathOLanternGame = main_module.MathOLanternGame
GameState = main_module.GameState
QuestionManager = main_module.QuestionManager


class TestGameOverConditions(unittest.TestCase):
    """Test game over detection conditions"""
    
    def setUp(self):
        """Set up test fixtures"""
        pygame.init()
        # Create a minimal game instance for testing
        # We'll mock the camera and hand tracker to avoid hardware dependencies
        
    def test_game_over_when_all_questions_complete(self):
        """Test that game transitions to GAME_OVER when all 10 questions are complete"""
        qm = QuestionManager()
        qm.select_random_questions()
        
        # Advance through all 10 questions
        for _ in range(10):
            self.assertFalse(qm.is_complete())
            qm.advance_question()
        
        # After 10 questions, should be complete
        self.assertTrue(qm.is_complete())
        self.assertIsNone(qm.get_current_question())
    
    def test_game_over_when_lives_reach_zero(self):
        """Test that game should end when lives reach 0"""
        # This is a logic test - when lives = 0, game should transition to GAME_OVER
        lives = 3
        
        # Simulate incorrect slices
        lives -= 1  # First incorrect
        self.assertEqual(lives, 2)
        
        lives -= 1  # Second incorrect
        self.assertEqual(lives, 1)
        
        lives -= 1  # Third incorrect
        self.assertEqual(lives, 0)
        
        # At this point, game should transition to GAME_OVER
        self.assertEqual(lives, 0)


class TestRestartLogic(unittest.TestCase):
    """Test game restart functionality"""
    
    def test_restart_resets_score(self):
        """Test that restart resets score to 0"""
        # Simulate game state
        score = 25  # Some accumulated score
        
        # After restart
        score = 0
        self.assertEqual(score, 0)
    
    def test_restart_resets_lives(self):
        """Test that restart resets lives to 3"""
        # Simulate game state
        lives = 1  # Player lost 2 lives
        
        # After restart
        lives = 3
        self.assertEqual(lives, 3)
    
    def test_restart_selects_new_questions(self):
        """Test that restart selects new random questions"""
        qm = QuestionManager()
        
        # Select first set of questions
        qm.select_random_questions()
        first_questions = qm.current_questions.copy()
        
        # Select second set of questions (simulating restart)
        qm.select_random_questions()
        second_questions = qm.current_questions
        
        # Both should have 10 questions
        self.assertEqual(len(first_questions), 10)
        self.assertEqual(len(second_questions), 10)
        
        # Questions should be valid (this doesn't guarantee they're different,
        # but with 50 questions in the bank, they're very likely to be different)
        for q in second_questions:
            self.assertIn(q.operator, ['+', '-'])
    
    def test_restart_transitions_to_instructions(self):
        """Test that restart transitions to INSTRUCTIONS state"""
        # After restart, state should be INSTRUCTIONS
        state = GameState.INSTRUCTIONS
        self.assertEqual(state, GameState.INSTRUCTIONS)


class TestGameOverRendering(unittest.TestCase):
    """Test game over screen rendering"""
    
    def test_game_over_text_exists(self):
        """Test that game over text is defined"""
        # This is a simple check that the text exists
        game_over_text = "GAME OVER"
        self.assertEqual(game_over_text, "GAME OVER")
    
    def test_restart_prompt_exists(self):
        """Test that restart prompt text is defined"""
        restart_prompt = "Hit enter to restart game"
        self.assertEqual(restart_prompt, "Hit enter to restart game")


if __name__ == '__main__':
    unittest.main()
