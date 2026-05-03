"""
Test script to verify the agentic RAG returns detailed responses with sources.
"""

from chatbot import ChatHandler

def test_detailed_response():
    """Test that responses include detailed sources with chunk IDs."""
    print("=" * 80)
    print("Testing Detailed Response with Sources")
    print("=" * 80)
    
    handler = ChatHandler()
    
    # Test question
    test_question = "My father was recently diagnosed and is in the early stages of dementia. He has always been very independent, but now he needs help with managing his medications and finances. However, he fiercely resists any help, insisting he is fine and accusing me of trying to take over his life. How can I approach him to accept necessary support without damaging our relationship?"
    
    print(f"\n📝 Question:\n{test_question}\n")
    
    response = handler.chat(test_question)
    
    print("=" * 80)
    print("RESPONSE:")
    print("=" * 80)
    print(f"\n{response['reply']}\n")
    
    print("=" * 80)
    print("REFERENCES:")
    print("=" * 80)
    if response['references']:
        for i, ref in enumerate(response['references'], 1):
            print(f"\n[Reference {i}]")
            print(f"  Chunk ID: {ref.get('chunk_id', 'N/A')}")
            print(f"  Source: {ref.get('source', 'Unknown')}")
            print(f"  Page: {ref.get('page', 'N/A')}")
            print(f"  Text: {ref.get('text', '')[:100]}...")
    else:
        print("No references found")
    
    print("\n" + "=" * 80)
    print("METADATA:")
    print("=" * 80)
    print(f"On Topic: {response['is_on_topic']}")
    print(f"Used Web Search: {response['used_web_search']}")
    print(f"Tone Detected: {response['tone_detected']}")
    print("=" * 80)

if __name__ == "__main__":
    test_detailed_response()
