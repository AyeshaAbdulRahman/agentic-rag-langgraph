"""
graph/nodes/emotional.py — Node 8: Emotional Tone Wrapping

The most important node for user experience!

Rewrites the factual answer with appropriate emotional tone based on
what tone_detect.py detected in the user's message.

Tone → Response style:
  - anxious: Reassuring, calming, supportive
  - sad: Compassionate, gentle, validating grief
  - frustrated: Validating struggle, practical advice
  - confused: Simple language, clear steps
  - calm: Warm, professional, informative
"""

from langchain_core.prompts import PromptTemplate
from llm_factory import get_llm
from graph.state import AgentState


def emotional_node(state: AgentState) -> AgentState:
    """
    Node 8: Emotional Response
    
    Wraps the factual answer with emotionally appropriate language
    matching the user's detected tone.
    
    Args:
        state: Current agent state (must have generation and user_tone filled)
        
    Returns:
        Updated state with final_answer filled
    """
    
    # Define tone-specific guidance
    tone_guidance = {
        'anxious': (
            "The user is worried and fearful. "
            "Start with reassurance and calm language. "
            "Emphasize they are not alone and help is available. "
            "Be gentle and supportive."
        ),
        'sad': (
            "The user is grieving or upset. "
            "Start with compassionate acknowledgment of their pain. "
            "Validate their feelings before providing information. "
            "Be gentle and empathetic."
        ),
        'frustrated': (
            "The user is overwhelmed and burnt out. "
            "Validate how hard this is. "
            "Be practical and concise. "
            "Focus on actionable advice, not lengthy explanations."
        ),
        'confused': (
            "The user is unsure or disoriented. "
            "Use simple, crystal-clear language. "
            "Break information into small, numbered steps. "
            "Avoid jargon."
        ),
        'calm': (
            "The user is asking neutrally and factually. "
            "Keep the tone professional and informative. "
            "Be clear and well-organized but NOT overly emotional. "
            "Minimal emotional wrapping - just add warmth, not drama."
        )
    }
    
    guidance = tone_guidance.get(state.user_tone, tone_guidance['calm'])
    
    # Build emotional wrapping prompt
    prompt_template = PromptTemplate(
        input_variables=["tone_guidance", "original_answer"],
        template="""You are a dementia care assistant.

Emotional context for this response:
{tone_guidance}

Original answer:
{original_answer}

Rewrite this answer to match the user's emotional state.
Rules:
- Keep ALL factual information intact
- Add emotional warmth only if needed (for anxious/sad/frustrated/confused tones)
- For calm/neutral tone: Keep it professional and clear. Add minimal emotional wrapping.
- Never add facts not in the original
- Never be patronizing or overly dramatic
- Match the energy level of the original tone guidance

Final response:"""
    )
    
    # Get LLM
    llm = get_llm()
    chain = prompt_template | llm
    
    # Generate emotionally aware response
    response = chain.invoke(
        {"tone_guidance": guidance, "original_answer": state.generation}
    )
    final_answer = response.content
    
    state.final_answer = final_answer.strip()
    
    return state


if __name__ == "__main__":
    # Quick test
    from graph.state import AgentState
    
    test_cases = [
        ("anxious", "Alzheimer's is a progressive neurodegenerative disease affecting memory and cognition."),
        ("sad", "Family members may need to adjust to changes in personality and behavior."),
        ("frustrated", "Caregiving requires patience and regular self-care breaks."),
        ("confused", "Dementia progresses through stages: early, middle, and late."),
        ("calm", "Memory loss in dementia differs from normal aging."),
    ]
    
    print("Testing Emotional Node:")
    print("=" * 60)
    
    for tone, answer in test_cases:
        state = AgentState(
            question="Tell me about dementia",
            corrected_question="Tell me about dementia",
            generation=answer,
            user_tone=tone
        )
        
        result = emotional_node(state)
        
        print(f"\n🎭 Tone: {tone.upper()}")
        print(f"Original: {answer}")
        print(f"Emotional: {result.final_answer[:100]}...")
