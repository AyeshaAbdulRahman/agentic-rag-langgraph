from graph.nodes.spell_check import spell_check_node
from graph.state import AgentState

test_cases = [
    "what is Ager state in dementia",  # should correct to "Anger" not "Age"
    "what is alzaimer",  # should correct to "alzheimer"
    "wht ar symtoms of demnetia",  # should correct typos but preserve "dementia"
    "korean people with dementia",  # should preserve "korean"
]

print("Testing Improved Spell Check with Medical Term Priority:")
print("=" * 70)

for test_input in test_cases:
    state = AgentState(question=test_input)
    corrected_state = spell_check_node(state)
    
    print(f"Original:  {test_input}")
    print(f"Corrected: {corrected_state.corrected_question}")
    print()
