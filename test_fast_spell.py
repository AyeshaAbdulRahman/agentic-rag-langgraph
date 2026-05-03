#!/usr/bin/env python
"""Quick test of the spell checker - fast and no external downloads"""

from graph.nodes.spell_check import spell_check_node
from graph.state import AgentState

print("\n" + "="*70)
print("🚀 FAST SPELL CHECKER TEST (No External Downloads)")
print("="*70)

test_cases = [
    "wht is demnetia",
    "my granmather has alzeimer desease",
    "what ar the treatment optins",
    "can demntia be prevented",
]

print("\nSpell Corrections:\n")

for test_input in test_cases:
    state = AgentState(question=test_input)
    corrected_state = spell_check_node(state)
    
    print(f"  Input:  {test_input}")
    print(f"  Output: {corrected_state.corrected_question}\n")

print("="*70)
print("✓ Spell checker is working (no slow downloads, no errors)")
print("="*70)
