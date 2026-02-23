#!/usr/bin/env python
"""
Test script to verify prompt builder and FAIX data formatting.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from backend.chatbot.agents import get_agent, retrieve_for_agent
from backend.chatbot.knowledge_base import KnowledgeBase
from backend.chatbot.prompt_builder import build_messages

def test_prompt_builder():
    """Test prompt builder with FAIX data."""
    print("=" * 60)
    print("Testing Prompt Builder")
    print("=" * 60)
    
    # Initialize knowledge base
    print("\n1. Initializing KnowledgeBase...")
    kb = KnowledgeBase()
    print(f"   [OK] KnowledgeBase loaded with {len(kb.faix_data)} data sections")
    
    # Test FAQ agent
    print("\n2. Testing FAQ agent...")
    agent = get_agent('faq')
    if not agent:
        print("   [ERROR] FAQ agent not found!")
        return False
    print(f"   [OK] FAQ agent loaded: {agent.id}")
    
    # Test context retrieval
    print("\n3. Testing context retrieval...")
    query = "What programs does FAIX offer?"
    context = retrieve_for_agent(
        agent_id='faq',
        user_text=query,
        knowledge_base=kb,
        intent='program_info',
        top_k=3
    )
    
    print(f"   [OK] Context retrieved with {len(context)} sections")
    for key in context.keys():
        if key == 'faix_data':
            print(f"     - {key}: {len(context[key])} data sections")
            print(f"       Available keys: {list(context[key].keys())}")
        else:
            print(f"     - {key}: {len(context[key])} documents")
    
    # Test building messages
    print("\n4. Testing message building...")
    messages = build_messages(
        agent=agent,
        user_message=query,
        history=[],
        context=context,
        intent='program_info',
        language_code='en'
    )
    
    print(f"   [OK] Built {len(messages)} messages")
    
    # Print each message
    for i, msg in enumerate(messages):
        print(f"\n   Message {i+1}:")
        print(f"     Role: {msg.get('role')}")
        content = msg.get('content', '')
        print(f"     Content length: {len(content)} chars")
        
        # Check for FAIX data
        if 'FAIX Information Context' in content:
            print(f"     [OK] Contains FAIX Information Context")
            # Print first 500 chars
            print(f"     Preview (first 500 chars):")
            preview = content[:500]
            # Remove non-ASCII characters
            preview = ''.join(char for char in preview if ord(char) < 128)
            print(f"     {preview}...")
        elif 'Staff Contacts Context' in content:
            print(f"     [OK] Contains Staff Contacts Context")
        else:
            # Print first 200 chars
            print(f"     Preview (first 200 chars):")
            preview = content[:200]
            # Remove non-ASCII characters
            preview = ''.join(char for char in preview if ord(char) < 128)
            print(f"     {preview}...")
    
    # Test with different queries
    print("\n5. Testing with different queries...")
    test_queries = [
        ("about_faix", "Tell me about FAIX"),
        ("staff_contact", "Who is the dean?"),
        ("program_info", "What is BAXI?"),
    ]
    
    for intent, query in test_queries:
        print(f"\n   Query: {query} (intent: {intent})")
        context = retrieve_for_agent(
            agent_id='faq',
            user_text=query,
            knowledge_base=kb,
            intent=intent,
            top_k=3
        )
        
        messages = build_messages(
            agent=agent,
            user_message=query,
            history=[],
            context=context,
            intent=intent,
            language_code='en'
        )
        
        # Check if FAIX data is in the messages
        has_faix_data = any('FAIX Information Context' in msg.get('content', '') for msg in messages)
        if has_faix_data:
            print(f"   [OK] FAIX data included in messages")
        else:
            print(f"   [WARNING] FAIX data not found in messages")
    
    print("\n" + "=" * 60)
    print("Prompt Builder Test Complete!")
    print("=" * 60)
    return True

if __name__ == "__main__":
    success = test_prompt_builder()
    sys.exit(0 if success else 1)
