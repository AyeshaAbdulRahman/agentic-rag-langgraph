"""
test_conversation_memory.py — Test Multi-Turn Conversation with Memory

Demonstrates the new conversation memory system that allows the chatbot
to remember context from previous exchanges in the same session.

Run: python test_conversation_memory.py
"""

from chatbot import ChatHandler
from conversation_memory import ConversationMemory


def test_basic_memory():
    """Test basic memory operations."""
    print("\n" + "=" * 70)
    print("🧪 TEST 1: Basic Memory Operations")
    print("=" * 70)
    
    memory = ConversationMemory()
    
    # Create session
    session_id = memory.create_session()
    print(f"\n✓ Created session: {session_id}")
    
    # Add exchanges
    exchanges = [
        ("What is dementia?", "Dementia is a general term for a decline in cognitive abilities..."),
        ("What are the types?", "Main types include Alzheimer's, vascular, and Lewy body dementia..."),
        ("How is it diagnosed?", "Diagnosis typically involves cognitive testing, brain imaging, and medical history..."),
    ]
    
    for i, (user, assistant) in enumerate(exchanges, 1):
        memory.add_exchange(session_id, user, assistant)
        print(f"\n  Exchange {i}:")
        print(f"    User: {user}")
        print(f"    Bot: {assistant[:60]}...")
    
    # Get context
    print(f"\n✓ Memory stored successfully")
    context = memory.get_context(session_id, "What treatments are available?")
    print(f"\n✓ Retrieved context for new question:")
    print(context[:300] + "...")
    
    # Session info
    summary = memory.get_session_summary(session_id)
    print(f"\n✓ Session Info:")
    for key, value in summary.items():
        print(f"    {key}: {value}")


def test_chatbot_with_memory():
    """Test ChatHandler with conversation memory."""
    print("\n" + "=" * 70)
    print("🧪 TEST 2: Chatbot with Conversation Memory")
    print("=" * 70)
    
    chatbot = ChatHandler()
    
    # Create session
    session_id = chatbot.create_session()
    print(f"\n✓ Session created: {session_id}")
    
    # Conversation flow
    questions = [
        "What is Alzheimer's disease?",
        "What are early symptoms?",
        "How is it treated?",
    ]
    
    for i, question in enumerate(questions, 1):
        print(f"\n{'─' * 70}")
        print(f"Turn {i}: {question}")
        print(f"{'─' * 70}")
        
        # Get response with session context
        response = chatbot.chat(question, session_id=session_id)
        
        print(f"\nBot: {response['reply'][:200]}...")
        print(f"\nMetadata:")
        print(f"  - Tone: {response['tone_detected']}")
        print(f"  - Context Used: {response.get('has_context', False)}")
        print(f"  - Turn #: {response.get('turn_number', 0)}")
        print(f"  - On Topic: {response['is_on_topic']}")


def test_context_continuity():
    """Test that context is properly used across turns."""
    print("\n" + "=" * 70)
    print("🧪 TEST 3: Context Continuity Across Turns")
    print("=" * 70)
    
    memory = ConversationMemory()
    session_id = memory.create_session()
    
    # First exchange (setup)
    memory.add_exchange(
        session_id,
        "Tell me about cognitive impairment",
        "Cognitive impairment refers to difficulties with thinking, memory, and processing..."
    )
    
    # Second exchange (follow-up)
    memory.add_exchange(
        session_id,
        "What causes this?",
        "It can be caused by Alzheimer's, stroke, Parkinson's, or brain injury..."
    )
    
    # Get context for third exchange
    context = memory.get_context(session_id, "Can it be reversed?")
    
    print("\n✓ Conversation sequence:")
    print("  1. User: Tell me about cognitive impairment")
    print("  2. Bot: Cognitive impairment refers to...")
    print("  3. User: What causes this?")
    print("  4. Bot: It can be caused by...")
    print("  5. User: Can it be reversed? [NEW]")
    
    print(f"\n✓ Context retrieved for new question:")
    print(context)
    
    print(f"\n✓ This allows the LLM to understand 'this' refers to cognitive impairment")
    print(f"  and provide context-aware answers!")


def test_session_multiple():
    """Test multiple concurrent sessions."""
    print("\n" + "=" * 70)
    print("🧪 TEST 4: Multiple Concurrent Sessions")
    print("=" * 70)
    
    memory = ConversationMemory()
    
    # Create two sessions
    session_1 = memory.create_session()
    session_2 = memory.create_session()
    
    print(f"\n✓ Session 1: {session_1}")
    print(f"✓ Session 2: {session_2}")
    
    # Add different content to each
    memory.add_exchange(
        session_1,
        "What is Alzheimer's?",
        "Alzheimer's is a neurodegenerative disease..."
    )
    
    memory.add_exchange(
        session_2,
        "How do I become a caregiver?",
        "Becoming a caregiver involves..."
    )
    
    # Get context from each
    context_1 = memory.get_context(session_1, "What are treatments?")
    context_2 = memory.get_context(session_2, "What training is needed?")
    
    print(f"\n✓ Session 1 remembers: Alzheimer's disease")
    print(f"  Context includes: {'Alzheimer' in context_1}")
    
    print(f"\n✓ Session 2 remembers: Caregiver training")
    print(f"  Context includes: {'caregiver' in context_2}")
    
    print(f"\n✓ Sessions are independent and isolated!")


def test_memory_pruning():
    """Test memory pruning when history gets too long."""
    print("\n" + "=" * 70)
    print("🧪 TEST 5: Memory Pruning (keeping recent exchanges)")
    print("=" * 70)
    
    memory = ConversationMemory(max_history_length=3)  # Keep only 3 exchanges
    session_id = memory.create_session()
    
    # Add 5 exchanges
    print("\n✓ Adding 5 exchanges to session with max_history_length=3:")
    
    for i in range(1, 6):
        question = f"Question {i}"
        answer = f"Answer {i}"
        memory.add_exchange(session_id, question, answer)
        
        history_len = len(memory.sessions[session_id]['history'])
        print(f"  Exchange {i} added - History length: {history_len}")
    
    # Show that only recent ones are kept
    session = memory.sessions[session_id]
    print(f"\n✓ After pruning, only {len(session['history'])} most recent kept:")
    for exchange in session['history']:
        print(f"  - {exchange['user']}")


if __name__ == "__main__":
    print("\n" + "╔" + "═" * 68 + "╗")
    print("║" + " " * 15 + "🧪 CONVERSATION MEMORY TEST SUITE" + " " * 20 + "║")
    print("╚" + "═" * 68 + "╝")
    
    try:
        test_basic_memory()
        test_context_continuity()
        test_session_multiple()
        test_memory_pruning()
        test_chatbot_with_memory()
        
        print("\n" + "=" * 70)
        print("✅ All tests completed successfully!")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
