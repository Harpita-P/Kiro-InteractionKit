#!/usr/bin/env python3
"""
Integration test for question selection and management workflow
"""

import os
import sys

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Import from the game
sys.path.insert(0, os.path.join(PROJECT_ROOT, 'my_apps', 'Math-O-Lantern'))
from main import QuestionManager


def test_complete_question_workflow():
    """Test the complete workflow of question selection and management"""
    print("Testing complete question workflow...")
    
    # Initialize question manager
    qm = QuestionManager()
    print(f"✓ Question bank initialized with {len(qm.question_bank)} questions")
    
    # Select random questions for a game session
    qm.select_random_questions()
    print(f"✓ Selected {len(qm.current_questions)} unique questions")
    
    # Verify uniqueness
    question_set = set()
    for q in qm.current_questions:
        question_tuple = (q.operand1, q.operator, q.operand2, q.answer)
        assert question_tuple not in question_set, "Duplicate question found!"
        question_set.add(question_tuple)
    print("✓ All selected questions are unique")
    
    # Simulate going through all questions
    question_count = 0
    while not qm.is_complete():
        current = qm.get_current_question()
        assert current is not None, "Current question should not be None"
        print(f"  Question {question_count + 1}: {current.get_expression()}")
        
        # Simulate timer countdown
        time_elapsed = 0
        while time_elapsed < 15.0:
            expired = qm.update_timer(1.0)
            time_elapsed += 1.0
            if expired:
                break
        
        assert qm.question_timer == 0, "Timer should be at 0 after expiration"
        
        # Advance to next question
        qm.advance_question()
        assert qm.question_timer == 15.0, "Timer should reset to 15 seconds"
        question_count += 1
    
    print(f"✓ Completed all {question_count} questions")
    assert question_count == 10, "Should have exactly 10 questions"
    
    # Verify completion
    assert qm.is_complete(), "Question manager should be complete"
    assert qm.get_current_question() is None, "No current question after completion"
    print("✓ Question manager correctly reports completion")
    
    print("\n✅ All workflow tests passed!")


if __name__ == '__main__':
    test_complete_question_workflow()
