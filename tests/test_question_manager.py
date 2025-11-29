#!/usr/bin/env python3
"""
Unit tests for Question and QuestionManager classes
"""

import os
import sys
import unittest

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Import from the game
sys.path.insert(0, os.path.join(PROJECT_ROOT, 'my_apps', 'Math-O-Lantern'))
from main import Question, QuestionManager


class TestQuestion(unittest.TestCase):
    """Test the Question dataclass"""
    
    def test_question_creation(self):
        """Test creating a Question instance"""
        q = Question(6, '+', 25, 31)
        self.assertEqual(q.operand1, 6)
        self.assertEqual(q.operator, '+')
        self.assertEqual(q.operand2, 25)
        self.assertEqual(q.answer, 31)
    
    def test_get_expression_addition(self):
        """Test get_expression for addition"""
        q = Question(6, '+', 25, 31)
        self.assertEqual(q.get_expression(), "6 + 25 = ?")
    
    def test_get_expression_subtraction(self):
        """Test get_expression for subtraction"""
        q = Question(14, '-', 9, 5)
        self.assertEqual(q.get_expression(), "14 - 9 = ?")


class TestQuestionManager(unittest.TestCase):
    """Test the QuestionManager class"""
    
    def test_initialization(self):
        """Test QuestionManager initialization"""
        qm = QuestionManager()
        self.assertEqual(len(qm.question_bank), 50)
        self.assertEqual(qm.current_index, 0)
        self.assertEqual(qm.question_timer, 15.0)
    
    def test_question_bank_operators(self):
        """Test that question bank contains only + and - operators"""
        qm = QuestionManager()
        for question in qm.question_bank:
            self.assertIn(question.operator, ['+', '-'])
    
    def test_question_bank_operand_range(self):
        """Test that operands are within 1-9999 range"""
        qm = QuestionManager()
        for question in qm.question_bank:
            self.assertGreaterEqual(question.operand1, 1)
            self.assertLessEqual(question.operand1, 999)  # Max 3 digits
            self.assertGreaterEqual(question.operand2, 1)
            self.assertLessEqual(question.operand2, 999)  # Max 3 digits
    
    def test_question_bank_correct_answers(self):
        """Test that all answers are calculated correctly"""
        qm = QuestionManager()
        for question in qm.question_bank:
            if question.operator == '+':
                expected = question.operand1 + question.operand2
            else:  # operator == '-'
                expected = question.operand1 - question.operand2
            self.assertEqual(question.answer, expected)
    
    def test_select_random_questions(self):
        """Test selecting 10 random questions"""
        qm = QuestionManager()
        qm.select_random_questions()
        self.assertEqual(len(qm.current_questions), 10)
        self.assertEqual(qm.current_index, 0)
        self.assertEqual(qm.question_timer, 15.0)
    
    def test_select_random_questions_unique(self):
        """Test that selected questions are unique"""
        qm = QuestionManager()
        qm.select_random_questions()
        # Check uniqueness by comparing question objects
        unique_questions = set()
        for q in qm.current_questions:
            question_tuple = (q.operand1, q.operator, q.operand2, q.answer)
            self.assertNotIn(question_tuple, unique_questions)
            unique_questions.add(question_tuple)
    
    def test_get_current_question(self):
        """Test getting the current question"""
        qm = QuestionManager()
        qm.select_random_questions()
        current = qm.get_current_question()
        self.assertIsNotNone(current)
        self.assertEqual(current, qm.current_questions[0])
    
    def test_get_current_question_when_complete(self):
        """Test getting current question when all are complete"""
        qm = QuestionManager()
        qm.select_random_questions()
        qm.current_index = 10  # Set to end
        current = qm.get_current_question()
        self.assertIsNone(current)
    
    def test_advance_question(self):
        """Test advancing to next question"""
        qm = QuestionManager()
        qm.select_random_questions()
        qm.question_timer = 5.0
        qm.advance_question()
        self.assertEqual(qm.current_index, 1)
        self.assertEqual(qm.question_timer, 15.0)
    
    def test_update_timer(self):
        """Test timer update"""
        qm = QuestionManager()
        qm.question_timer = 15.0
        expired = qm.update_timer(5.0)
        self.assertFalse(expired)
        self.assertEqual(qm.question_timer, 10.0)
    
    def test_update_timer_expiration(self):
        """Test timer expiration"""
        qm = QuestionManager()
        qm.question_timer = 2.0
        expired = qm.update_timer(3.0)
        self.assertTrue(expired)
        self.assertEqual(qm.question_timer, 0)
    
    def test_is_complete(self):
        """Test checking if all questions are complete"""
        qm = QuestionManager()
        qm.select_random_questions()
        self.assertFalse(qm.is_complete())
        qm.current_index = 10
        self.assertTrue(qm.is_complete())


if __name__ == '__main__':
    unittest.main()
