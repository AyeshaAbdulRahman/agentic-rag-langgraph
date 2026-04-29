#!/usr/bin/env python3
"""Quick test script to verify chatbot works."""

from chatbot import ChatHandler

print("✓ ChatHandler imported successfully\n")

try:
    print("⏳ Initializing ChatHandler...")
    chatbot = ChatHandler()
    print("✓ ChatHandler initialized!\n")
    
    # Test question
    test_question = "What is dementia?"
    print(f"Testing with: '{test_question}'\n")
    print("⏳ Calling chatbot.chat()...\n")
    
    response = chatbot.chat(test_question)
    
    print("=" * 60)
    print(f"✓ Response received!\n")
    print(f"Reply: {response['reply']}\n")
    print(f"On-topic: {response['is_on_topic']}")
    print(f"Tone: {response['tone_detected']}")
    print(f"Used web search: {response['used_web_search']}")
    if response['references']:
        print(f"References: {len(response['references'])} sources")
    print("=" * 60)
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
