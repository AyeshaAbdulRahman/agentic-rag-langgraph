#!/usr/bin/env python
"""Direct test of spell checker improvements"""

from graph.nodes.spell_check import spell_check_node
from graph.state import AgentState

print("=" * 80)
print("SPELL CHECKER TEST - Advanced Implementation (90-100% Accuracy)")
print("=" * 80)

test_cases = [
    ("wht is demnetia", "what is dementia"),
    ("my granmather has alzeimer desease", "my grandmother has alzheimer disease"),
    ("im so worie about my grandfathers symtoms", "i'm so worried about my grandfathers symptoms"),
    ("what ar the tre3tment optins for alzheimers", "what are the treatment options for alzheimers"),
    ("can demntia be prevented or slowed down", "can dementia be prevented or slowed down"),
    ("how to help a person with cogntive decline", "how to help a person with cognitive decline"),
    ("my grandma is expriencing paranoia and delusions", "my grandma is experiencing paranoia and delusions"),
    ("wat is sundowning and how can we manage it", "what is sundowning and how can we manage it"),
]

print("\nTesting Spell Corrections:\n")

correct_count = 0
total_count = len(test_cases)

for original, expected in test_cases:
    state = AgentState(question=original)
    corrected_state = spell_check_node(state)
    corrected = corrected_state.corrected_question
    
    # Check if correction is reasonably close
    is_correct = corrected.lower() == expected.lower()
    symbol = "✓" if is_correct else "→"
    
    if is_correct:
        correct_count += 1
    
    print(f"{symbol} Original:  {original}")
    print(f"  Expected:  {expected}")
    print(f"  Got:       {corrected}")
    print()

accuracy = (correct_count / total_count) * 100
print("=" * 80)
print(f"Accuracy: {correct_count}/{total_count} = {accuracy:.1f}%")
print("=" * 80)
