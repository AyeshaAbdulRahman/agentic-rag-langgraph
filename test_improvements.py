from chatbot import ChatHandler

print("\n" + "="*60)
print("🧠 NeuroCare AI — Test with Spell Check & Web Search")
print("="*60 + "\n")

try:
    ch = ChatHandler()
    print("✓ Chatbot initialized!\n")
    
    # Test 1: Misspelled question
    print("Test 1: Misspelled input")
    print("-" * 60)
    q1 = "wht causes memry loss in alzeimer"
    print(f"You: {q1}")
    response = ch.chat(q1)
    print(f"✏️  Corrected: {response.get('corrected_question')}\n")
    print(f"Bot: {response['reply'][:150]}...\n")
    
    # Test 2: Off-topic question
    print("\nTest 2: Off-topic question")
    print("-" * 60)
    q2 = "how do i cook pasta"
    print(f"You: {q2}")
    response = ch.chat(q2)
    print(f"Bot: {response['reply']}\n")
    
    print("="*60)
    print("✓ All tests completed!")
    print("="*60)
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
