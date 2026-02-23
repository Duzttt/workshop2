#!/usr/bin/env python
"""
Test script to verify database knowledge base works correctly.
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_app.settings')
import django
django.setup()

from backend.chatbot.knowledge_base_db import KnowledgeBaseDB


def test_db_knowledge_base():
    """Test database knowledge base."""
    print("=" * 60)
    print("Testing Database Knowledge Base")
    print("=" * 60)
    
    kb = KnowledgeBaseDB()
    
    # Test 1: Program query
    print("\n1. Testing program query...")
    answer = kb.get_answer('program_info', 'What programs does FAIX offer?')
    if answer:
        print(f"   [OK] Answer retrieved ({len(answer)} chars)")
        print(f"   Preview: {answer[:150]}...")
    else:
        print("   [ERROR] No answer retrieved")
    
    # Test 2: About FAIX query
    print("\n2. Testing about FAIX query...")
    answer = kb.get_answer('about_faix', 'Tell me about FAIX')
    if answer:
        print(f"   [OK] Answer retrieved ({len(answer)} chars)")
        print(f"   Preview: {answer[:150]}...")
    else:
        print("   [ERROR] No answer retrieved")
    
    # Test 3: Dean query
    print("\n3. Testing dean query...")
    answer = kb.get_answer('staff_contact', 'Who is the dean?')
    if answer:
        print(f"   [OK] Answer retrieved ({len(answer)} chars)")
        print(f"   Preview: {answer[:150]}...")
    else:
        print("   [ERROR] No answer retrieved")
    
    # Test 4: Specific program query
    print("\n4. Testing specific program query...")
    answer = kb.get_answer('program_info', 'What is BAXI?')
    if answer:
        print(f"   [OK] Answer retrieved ({len(answer)} chars)")
        print(f"   Preview: {answer[:150]}...")
    else:
        print("   [ERROR] No answer retrieved")
    
    # Test 5: Admission query
    print("\n5. Testing admission query...")
    answer = kb.get_answer('admission', 'What are the admission requirements?')
    if answer:
        print(f"   [OK] Answer retrieved ({len(answer)} chars)")
        print(f"   Preview: {answer[:150]}...")
    else:
        print("   [ERROR] No answer retrieved")
    
    # Test 6: Get documents for RAG
    print("\n6. Testing get_documents for RAG...")
    documents = kb.get_documents('program_info', 'What programs does FAIX offer?', top_k=3)
    if documents:
        print(f"   [OK] Retrieved {len(documents)} documents")
        for i, doc in enumerate(documents):
            print(f"     Document {i+1}: {doc['source']} (score: {doc['score']})")
    else:
        print("   [ERROR] No documents retrieved")
    
    print("\n" + "=" * 60)
    print("Database Knowledge Base Test Complete!")
    print("=" * 60)
    return True


if __name__ == "__main__":
    success = test_db_knowledge_base()
    sys.exit(0 if success else 1)
