#!/usr/bin/env python
"""
Test script to verify FAIX data is loading correctly.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from backend.chatbot.agents import _get_faix_data_for_faq
from backend.chatbot.knowledge_base import KnowledgeBase

def test_data_loading():
    """Test that FAIX data loads correctly."""
    print("=" * 60)
    print("Testing FAIX Data Loading")
    print("=" * 60)
    
    # Test 1: Load FAIX data for FAQ agent
    print("\n1. Testing _get_faix_data_for_faq()...")
    try:
        faix_data = _get_faix_data_for_faq()
        if faix_data:
            print(f"   [OK] Successfully loaded {len(faix_data)} data sections")
            for key in faix_data.keys():
                print(f"     - {key}")
        else:
            print("   [ERROR] No data loaded!")
            return False
    except Exception as e:
        print(f"   [ERROR] Error loading FAIX data: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 2: Check specific data sections
    print("\n2. Checking specific data sections...")
    
    # Check faculty_info
    if 'faculty_info' in faix_data:
        faculty = faix_data['faculty_info']
        print(f"   [OK] Faculty Info loaded:")
        print(f"     - Name: {faculty.get('name', 'N/A')}")
        print(f"     - Dean: {faculty.get('dean', 'N/A')}")
        print(f"     - Established: {faculty.get('established', 'N/A')}")
    else:
        print("   [ERROR] faculty_info not found!")
    
    # Check programmes
    if 'programmes' in faix_data:
        programs = faix_data['programmes']
        print(f"   [OK] Programmes loaded:")
        if 'undergraduate' in programs:
            print(f"     - Undergraduate: {len(programs['undergraduate'])} programs")
            for prog in programs['undergraduate']:
                print(f"       * {prog.get('name', 'N/A')} ({prog.get('code', 'N/A')})")
        if 'postgraduate' in programs:
            print(f"     - Postgraduate: {len(programs['postgraduate'])} programs")
            for prog in programs['postgraduate']:
                print(f"       * {prog.get('name', 'N/A')} ({prog.get('code', 'N/A')})")
    else:
        print("   [ERROR] programmes not found!")
    
    # Test 3: Test KnowledgeBase
    print("\n3. Testing KnowledgeBase...")
    try:
        kb = KnowledgeBase()
        print(f"   [OK] KnowledgeBase initialized")
        print(f"     - FAIX data sections: {len(kb.faix_data) if kb.faix_data else 0}")
        
        # Test getting an answer
        print("\n4. Testing get_answer()...")
        test_questions = [
            ("program_info", "What programs does FAIX offer?"),
            ("about_faix", "Tell me about FAIX"),
            ("staff_contact", "Who is the dean?"),
        ]
        
        for intent, question in test_questions:
            print(f"\n   Question: {question}")
            print(f"   Intent: {intent}")
            answer = kb.get_answer(intent, question)
            if answer:
                print(f"   [OK] Answer retrieved ({len(answer)} chars)")
                print(f"     Preview: {answer[:100]}...")
            else:
                print(f"   [ERROR] No answer retrieved")
        
    except Exception as e:
        print(f"   [ERROR] Error testing KnowledgeBase: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n" + "=" * 60)
    print("Data Loading Test Complete!")
    print("=" * 60)
    return True

if __name__ == "__main__":
    success = test_data_loading()
    sys.exit(0 if success else 1)
