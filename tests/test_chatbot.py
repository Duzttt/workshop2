"""
Test script for KnowledgeBase functionality.
Tests that the knowledge base can load FAIX data and retrieve answers.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from backend.chatbot.knowledge_base import KnowledgeBase


def test_knowledge_base_initialization():
    """Test that KnowledgeBase initializes correctly."""
    print("Test 1: KnowledgeBase initialization")
    kb = KnowledgeBase()
    assert kb is not None, "KnowledgeBase should be initialized"
    assert kb.faix_data is not None, "FAIX data should be loaded"
    assert len(kb.faix_data) > 0, "FAIX data should not be empty"
    print("[OK] KnowledgeBase initialized successfully")
    print(f"  Loaded {len(kb.faix_data)} data sections")


def test_program_info_retrieval():
    """Test retrieving program information."""
    print("\nTest 2: Program information retrieval")
    kb = KnowledgeBase()
    
    # Test program query
    intent = "program_info"
    user_question = "What programs does FAIX offer?"
    answer = kb.get_answer(intent, user_question)
    
    assert answer is not None, "Answer should not be None"
    assert len(answer) > 0, "Answer should not be empty"
    assert "program" in answer.lower() or "BAXI" in answer or "BAXZ" in answer, \
        "Answer should contain program information"
    
    print("[OK] Program information retrieved successfully")
    print(f"  Question: {user_question}")
    print(f"  Answer length: {len(answer)} chars")
    print(f"  Preview: {answer[:100]}...")


def test_about_faix_retrieval():
    """Test retrieving FAIX information."""
    print("\nTest 3: FAIX information retrieval")
    kb = KnowledgeBase()
    
    # Test about FAIX query
    intent = "about_faix"
    user_question = "Tell me about FAIX"
    answer = kb.get_answer(intent, user_question)
    
    assert answer is not None, "Answer should not be None"
    assert len(answer) > 0, "Answer should not be empty"
    assert "FAIX" in answer or "Faculty" in answer, \
        "Answer should contain FAIX information"
    
    print("[OK] FAIX information retrieved successfully")
    print(f"  Question: {user_question}")
    print(f"  Answer length: {len(answer)} chars")
    print(f"  Preview: {answer[:100]}...")


def test_dean_retrieval():
    """Test retrieving dean information."""
    print("\nTest 4: Dean information retrieval")
    kb = KnowledgeBase()
    
    # Test dean query
    intent = "staff_contact"
    user_question = "Who is the dean?"
    answer = kb.get_answer(intent, user_question)
    
    assert answer is not None, "Answer should not be None"
    assert len(answer) > 0, "Answer should not be empty"
    assert "dean" in answer.lower() or "Muhammad" in answer, \
        "Answer should contain dean information"
    
    print("[OK] Dean information retrieved successfully")
    print(f"  Question: {user_question}")
    print(f"  Answer length: {len(answer)} chars")
    print(f"  Preview: {answer[:100]}...")


def test_program_details_retrieval():
    """Test retrieving specific program details."""
    print("\nTest 5: Specific program details retrieval")
    kb = KnowledgeBase()
    
    # Test specific program query
    intent = "program_info"
    user_question = "What is BAXI?"
    answer = kb.get_answer(intent, user_question)
    
    assert answer is not None, "Answer should not be None"
    assert len(answer) > 0, "Answer should not be empty"
    assert "BAXI" in answer or "Bachelor" in answer, \
        "Answer should contain BAXI program details"
    
    print("[OK] Specific program details retrieved successfully")
    print(f"  Question: {user_question}")
    print(f"  Answer length: {len(answer)} chars")
    print(f"  Preview: {answer[:100]}...")


def main():
    """Run all tests."""
    print("=" * 60)
    print("Testing KnowledgeBase")
    print("=" * 60)
    
    try:
        test_knowledge_base_initialization()
        test_program_info_retrieval()
        test_about_faix_retrieval()
        test_dean_retrieval()
        test_program_details_retrieval()
        
        print("\n" + "=" * 60)
        print("All tests passed! [OK]")
        print("=" * 60)
        return True
    except AssertionError as e:
        print(f"\n[ERROR] Test failed: {e}")
        return False
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
