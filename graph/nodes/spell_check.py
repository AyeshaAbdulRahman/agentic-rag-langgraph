"""
graph/nodes/spell_check.py — Node 1: Spell Checking & Auto-Correction

Auto-corrects spelling mistakes in user queries while preserving
medical terminology like Alzheimer's, dementia, caregiving, etc.

Uses: pyspellchecker with custom medical dictionary
"""

import re
from spellchecker import SpellChecker
from difflib import SequenceMatcher
from graph.state import AgentState


# Medical and dementia-related terms that shouldn't be corrected
MEDICAL_TERMS = {
    'alzheimer', 'alzheimers', 'dementia', 'caregiving', 'caregiver',
    'memory', 'cognitive', 'neurological', 'vascular', 'lewy', 'bodies',
    'frontotemporal', 'parkinson', 'parkinsons', 'plaques', 'tangles',
    'neurodegeneration', 'neurofibrillary', 'amyloid', 'tau', 'brain',
    'neurological', 'progression', 'syndrome', 'mnci', 'mci', 'symptoms',
    'neuropsychological', 'behavioral', 'psychiatric', 'medication',
    'acetylcholinesterase', 'inhibitor', 'memantine', 'donepezil',
    'rivastigmine', 'galantamine', 'aricept', 'exelon', 'razadyne',
    'namenda', 'hospice', 'palliative', 'caregiver', 'caregiver',
    'caregiving', 'memory', 'confusion', 'anxiety', 'depression',
    'wandering', 'sundowning', 'agitation', 'aggression', 'apathy',
    # Behavioral and emotional terms
    'anger', 'irritability', 'hallucinations', 'delusions', 'paranoia',
    'suspicion', 'restlessness', 'sleep', 'insomnia', 'sleeplessness',
    'eating', 'eating', 'appetite', 'incontinence', 'disinhibition',
    'repetition', 'repetitive', 'hoarding', 'accusations', 'accusations',
    'screaming', 'yelling', 'hitting', 'biting', 'scratching',
    'wandering', 'getting', 'lost', 'disorientation', 'confusion',
    'recognizing', 'recognition', 'faces', 'names', 'family',
    # Age and demographic terms
    'age', 'aged', 'aging', 'elderly', 'older', 'korean', 'asian',
    'gender', 'male', 'female', 'race', 'ethnicity',
}


def similarity_score(a, b):
    """Calculate string similarity (0-1)."""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def spell_check_node(state: AgentState) -> AgentState:
    """
    Node 1: Spell Check
    
    Automatically corrects spelling mistakes while preserving medical terms.
    Only corrects obvious typos (high similarity to known words).
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with corrected_question filled
    """
    
    # Initialize spell checker
    spell = SpellChecker()
    
    # Get the raw question
    question = state.question.strip()
    
    if not question:
        state.corrected_question = ""
        return state
    
    # Tokenize into words (preserve case info)
    words = re.findall(r'\b[a-zA-Z]+\b|\W+', question)
    
    corrected_words = []
    for token in words:
        # Skip non-letter tokens
        if not any(c.isalpha() for c in token):
            corrected_words.append(token)
            continue
        
        # Check if word is in medical dictionary
        token_lower = token.lower()
        if token_lower in MEDICAL_TERMS:
            # Medical term - keep as is
            corrected_words.append(token)
            continue
        
        # Check if it's a known word
        if token_lower in spell:
            corrected_words.append(token)
            continue
        
        # Not a known word - find best match
        # First check if it's similar to a medical term
        best_match = None
        best_score = 0.70  # threshold for similarity
        
        for med_term in MEDICAL_TERMS:
            score = similarity_score(token, med_term)
            if score > best_score:
                best_score = score
                best_match = med_term
        
        # If found good match in medical terms, use it
        if best_match:
            if token[0].isupper():
                corrected = best_match[0].upper() + best_match[1:]
            else:
                corrected = best_match.lower()
            corrected_words.append(corrected)
        else:
            # Otherwise try generic spell correction
            corrected = spell.correction(token)
            
            if corrected and corrected.lower() != token.lower():
                similarity = similarity_score(token, corrected)
                
                # Only apply if similarity is high
                if similarity >= 0.75:
                    if token[0].isupper():
                        corrected = corrected[0].upper() + corrected[1:]
                    else:
                        corrected = corrected.lower()
                    corrected_words.append(corrected)
                else:
                    # Low similarity - keep original
                    corrected_words.append(token)
            else:
                corrected_words.append(token)
    
    # Reconstruct the sentence
    state.corrected_question = ''.join(corrected_words)
    
    return state


if __name__ == "__main__":
    # Quick test
    from graph.state import AgentState
    
    test_cases = [
        "wht is demnetia",
        "my granmather has alzeimer desease",
        "im so worie about symptoms",
    ]
    
    print("Testing Spell Check Node:")
    print("=" * 60)
    
    for test_input in test_cases:
        state = AgentState(question=test_input)
        result = spell_check_node(state)
        print(f"Input:  {test_input}")
        print(f"Output: {result.corrected_question}")
        print()
