import sys
import json

from chatbot import ChatHandler

print("\n" + "="*60)
print("🧠 NeuroCare AI Chatbot Test")
print("="*60 + "\n")

try:
    print("⏳ Initializing chatbot...")
    ch = ChatHandler()
    print("✓ Chatbot initialized!\n")
    
    test_question = "What is dementia?"
    print(f"Question: {test_question}\n")
    print("⏳ Processing (this may take a minute)...\n")
    
    response = ch.chat(test_question)
    
    print("="*60)
    print("✓ RESPONSE RECEIVED!\n")
    print(f"Reply:\n{response.get('reply', 'NO REPLY')}\n")
    print(f"On-topic: {response.get('is_on_topic')}")
    print(f"Tone: {response.get('tone_detected')}")
    print(f"Web search used: {response.get('used_web_search')}")
    print(f"References: {len(response.get('references', []))} sources")
    if response.get('references'):
        print("\nTop source:")
        ref = response['references'][0]
        print(f"  - {ref['source']} (p. {ref.get('page', 'N/A')})")
    print("="*60 + "\n")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
