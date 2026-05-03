"""
Test script to verify spell check fixes
"""

from graph.nodes.spell_check import spell_check_node
from graph.state import AgentState

def test_spell_check():
    """Test that spell checker doesn't make wrong corrections."""
    print("=" * 80)
    print("Testing Spell Checker Fix")
    print("=" * 80)
    
    test_cases = [
        ("which type of comunication", "which type of communication"),  # Should fix typo
        ("what is dementia", "what is dementia"),  # Already correct
        ("my granmother has memory loss", "my grandmother has memory loss"),  # Simple fix
        ("I am confuzed about dementia", "I am confused about dementia"),  # Fix confused
    ]
    
    for original, expected in test_cases:
        state = AgentState(question=original)
        result = spell_check_node(state)
        corrected = result.corrected_question
        
        status = "✅" if corrected.lower() == expected.lower() else "❌"
        print(f"\n{status} Original:  '{original}'")
        print(f"   Expected:  '{expected}'")
        print(f"   Got:       '{corrected}'")
        
        if corrected.lower() != expected.lower():
            print(f"   ⚠️  MISMATCH!")

if __name__ == "__main__":
    test_spell_check()
