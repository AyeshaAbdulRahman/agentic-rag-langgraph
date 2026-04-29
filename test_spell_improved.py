from graph.nodes.spell_check import spell_check_node
from graph.state import AgentState

test_cases = [
    "wht is alzaimer",  # should correct to "what is alzheimer"
    "what is claimer",  # should NOT touch "claimer" (real word, even if wrong context)
    "wht ar symtoms of demnetia",  # should correct typos but preserve "dementia"
    "memry loss in alzeimer disease",  # should preserve both medical terms
]

print("Testing Improved Spell Check:")
print("=" * 70)

for test_input in test_cases:
    state = AgentState(question=test_input)
    corrected_state = spell_check_node(state)
    
    print(f"Original:  {test_input}")
    print(f"Corrected: {corrected_state.corrected_question}")
    print()
