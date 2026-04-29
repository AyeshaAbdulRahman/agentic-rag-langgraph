"""
graph/nodes/tone_detect.py — Node 2: Emotional Tone Detection

Detects the user's emotional tone from their message.
The detected tone is used later by the emotional.py node to craft appropriate responses.

Tones: anxious, sad, frustrated, confused, calm
"""

from langchain_core.prompts import PromptTemplate
from llm_factory import get_llm
from graph.state import AgentState


def tone_detect_node(state: AgentState) -> AgentState:
    """
    Node 2: Tone Detection
    
    Analyzes the corrected question to detect emotional tone.
    This tone is used later to emotionally-tune the response.
    
    Detected tones:
      - anxious: Worried, fearful about symptoms/future
      - sad: Grieving, upset about loss/change
      - frustrated: Overwhelmed, burnt out, impatient
      - confused: Unsure, disoriented, asking for clarification
      - calm: Neutral, informational query
    
    Args:
        state: Current agent state (must have corrected_question filled)
        
    Returns:
        Updated state with user_tone filled
    """
    
    # Build prompt for tone detection
    prompt_template = PromptTemplate(
        input_variables=["message"],
        template="""Analyze the emotional tone of this message from a dementia caregiver or patient:

"{message}"

Classify into ONE tone:
- anxious: Worried, fearful, scared about future/symptoms ("I'm worried...", "I'm scared...")
- sad: Grieving, upset, emotional pain ("I'm devastated...", "It's so sad...")
- frustrated: Overwhelmed, burnt out, impatient ("I'm exhausted...", "This is too much...")
- confused: Disoriented, asking for clarification because they don't understand ("I don't understand...", "Can you explain...")
- calm: Neutral, factual, just asking for information ("What is...", "Tell me about...", "How does...")

IMPORTANT:
- Simple factual questions like "What is dementia?" = CALM (not confused)
- Only use 'confused' if they express confusion/not understanding
- Default to CALM for informational queries

Reply with ONLY the single word. No explanation."""
    )
    
    # Get LLM and run chain
    llm = get_llm()
    chain = prompt_template | llm
    
    # Get the tone
    tone_response = chain.invoke({"message": state.corrected_question})
    tone = tone_response.content.strip().lower()
    
    # Validate and fallback to 'calm' if invalid
    valid_tones = ['anxious', 'sad', 'frustrated', 'confused', 'calm']
    if tone not in valid_tones:
        tone = 'calm'
    
    state.user_tone = tone
    
    return state


if __name__ == "__main__":
    # Quick test
    from graph.state import AgentState
    
    test_messages = [
        "I'm so worried about my mother's memory loss",
        "My husband doesn't recognize me anymore",
        "I'm exhausted caring for her day and night",
        "What are the early signs of dementia?",
        "I don't understand what's happening to my dad",
    ]
    
    print("Testing Tone Detection Node:")
    print("=" * 60)
    
    for msg in test_messages:
        state = AgentState(question=msg, corrected_question=msg)
        result = tone_detect_node(state)
        print(f"Message: {msg}")
        print(f"Tone:    {result.user_tone}")
        print()
