#!/usr/bin/env python
"""
Test script to verify LLM integration and data usage.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from backend.chatbot.agents import get_agent, retrieve_for_agent
from backend.chatbot.knowledge_base import KnowledgeBase
from backend.chatbot.prompt_builder import build_messages
from backend.llm.llm_client import get_llm_client, LLMError

def test_llm_integration():
    """Test LLM integration with FAIX data."""
    print("=" * 60)
    print("Testing LLM Integration")
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
    test_queries = [
        "What programs does FAIX offer?",
        "Tell me about FAIX",
        "Who is the dean?",
    ]
    
    for query in test_queries:
        print(f"\n   Query: {query}")
        context = retrieve_for_agent(
            agent_id='faq',
            user_text=query,
            knowledge_base=kb,
            intent='program_info',
            top_k=3
        )
        
        if context:
            print(f"   [OK] Context retrieved with {len(context)} sections")
            for key in context.keys():
                if key == 'faix_data':
                    print(f"     - {key}: {len(context[key])} data sections")
                else:
                    print(f"     - {key}: {len(context[key])} documents")
        else:
            print(f"   [WARNING] No context retrieved")
    
    # Test building messages
    print("\n4. Testing message building...")
    for query in test_queries:
        print(f"\n   Query: {query}")
        context = retrieve_for_agent(
            agent_id='faq',
            user_text=query,
            knowledge_base=kb,
            intent='program_info',
            top_k=3
        )
        
        messages = build_messages(
            agent=agent,
            user_message=query,
            history=[],
            context=context,
            intent='program_info',
            language_code='en'
        )
        
        print(f"   [OK] Built {len(messages)} messages")
        
        # Check if FAIX data is in the context
        has_faix_data = any('faix_data' in str(msg.get('content', '')) for msg in messages)
        if has_faix_data:
            print(f"   [OK] FAIX data included in context")
        else:
            print(f"   [WARNING] FAIX data not found in context")
    
    # Test LLM call (if available)
    print("\n5. Testing LLM call...")
    try:
        llm_client = get_llm_client()
        if llm_client:
            print(f"   [OK] LLM client initialized")
            
            # Test with a simple query
            test_query = "What programs does FAIX offer?"
            context = retrieve_for_agent(
                agent_id='faq',
                user_text=test_query,
                knowledge_base=kb,
                intent='program_info',
                top_k=3
            )
            
            messages = build_messages(
                agent=agent,
                user_message=test_query,
                history=[],
                context=context,
                intent='program_info',
                language_code='en'
            )
            
            print(f"   [OK] Calling LLM with {len(messages)} messages...")
            try:
                response = llm_client.chat(messages, max_tokens=200, temperature=0.5)
                print(f"   [OK] LLM response received ({len(response.content)} chars)")
                print(f"     Preview: {response.content[:200]}...")
            except LLMError as e:
                print(f"   [WARNING] LLM error: {e}")
                print(f"   [INFO] This is expected if Ollama is not running")
        else:
            print(f"   [WARNING] LLM client not available")
    except Exception as e:
        print(f"   [WARNING] Could not test LLM: {e}")
        print(f"   [INFO] This is expected if Ollama is not running or LLM is disabled")
    
    print("\n" + "=" * 60)
    print("LLM Integration Test Complete!")
    print("=" * 60)
    return True

if __name__ == "__main__":
    success = test_llm_integration()
    sys.exit(0 if success else 1)
