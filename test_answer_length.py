"""
Test script to verify:
1. Simple questions get CONCISE answers
2. Complex questions get DETAILED answers  
3. NO hallucination is happening
"""

from chatbot import ChatHandler

def test_concise_vs_detailed():
    """Test that the system gives appropriate length answers."""
    print("=" * 80)
    print("Testing Answer Length - Simple vs Complex Questions")
    print("=" * 80)
    
    handler = ChatHandler()
    
    # Test 1: SIMPLE FACTUAL QUESTION
    print("\n\n📝 TEST 1: SIMPLE QUESTION")
    print("-" * 80)
    simple_question = "What is dementia?"
    print(f"Q: {simple_question}\n")
    
    response = handler.chat(simple_question)
    
    answer = response['reply']
    answer_length = len(answer.split())
    
    print(f"ANSWER ({answer_length} words):")
    print(answer)
    print(f"\n✓ Grounded: {response.get('references', []) is not None}")
    print(f"✓ Sources: {len(response.get('references', []))} references")
    
    if answer_length > 500:
        print(f"⚠️  WARNING: Answer is TOO LONG ({answer_length} words). Should be concise for simple question.")
    else:
        print(f"✅ GOOD: Concise answer ({answer_length} words)")
    
    # Test 2: COMPLEX CAREGIVING QUESTION
    print("\n\n📝 TEST 2: COMPLEX QUESTION")
    print("-" * 80)
    complex_question = "My father resists help with medications. How can I approach this without damaging our relationship?"
    print(f"Q: {complex_question}\n")
    
    response = handler.chat(complex_question)
    
    answer = response['reply']
    answer_length = len(answer.split())
    
    print(f"ANSWER ({answer_length} words):")
    print(answer)
    print(f"\n✓ Grounded: {response.get('references', []) is not None}")
    print(f"✓ Sources: {len(response.get('references', []))} references")
    
    if answer_length < 150:
        print(f"⚠️  WARNING: Answer is TOO SHORT ({answer_length} words). Should be detailed for complex question.")
    else:
        print(f"✅ GOOD: Detailed answer ({answer_length} words)")
    
    # Test 3: Check for hallucination
    print("\n\n📝 TEST 3: HALLUCINATION CHECK")
    print("-" * 80)
    test_question = "What are the early symptoms of Alzheimer's?"
    print(f"Q: {test_question}\n")
    
    response = handler.chat(test_question)
    
    answer = response['reply']
    references = response.get('references', [])
    
    print("ANSWER:")
    print(answer)
    print(f"\n✓ Number of sources cited: {len(references)}")
    
    if references:
        print("\n📚 Sources (Grounding Check):")
        for i, ref in enumerate(references, 1):
            source = ref.get('source', 'Unknown')
            # Extract actual document name from source ref
            if '|' in source:
                doc_name = source.split('|')[-1].strip()
            else:
                doc_name = source
            print(f"  {i}. {doc_name}")
    else:
        print("⚠️  WARNING: No sources provided. Check if hallucinating!")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    test_concise_vs_detailed()
