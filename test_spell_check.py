from graph.nodes.spell_check import spell_check_node
from graph.state import AgentState

# Test with misspelled input
test_input = 'wht is demnetia and alzeimer'
state = AgentState(question=test_input)
corrected_state = spell_check_node(state)

print(f'Original: {state.question}')
print(f'Corrected: {corrected_state.corrected_question}')
