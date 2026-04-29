"""
llm_factory.py — LLM Provider Factory

Single function get_llm() that returns either Mistral or OpenAI based on config.
All 8 nodes call this function — no LLM config repeated anywhere.
"""

from langchain_mistralai import ChatMistralAI
from langchain_openai import ChatOpenAI
from config import (
    LLM_PROVIDER,
    MISTRAL_API_KEY,
    MISTRAL_MODEL,
    OPENAI_API_KEY,
    OPENAI_MODEL,
    LLM_TEMPERATURE,
    LLM_MAX_TOKENS
)


def get_llm():
    """
    Returns the configured LLM instance.
    
    If LLM_PROVIDER='mistral' → returns ChatMistralAI (free)
    If LLM_PROVIDER='openai'  → returns ChatOpenAI (paid)
    
    Raises:
        ValueError: If LLM_PROVIDER is invalid or API key is missing
        
    Returns:
        ChatMistralAI or ChatOpenAI instance
    """
    
    if LLM_PROVIDER == 'mistral':
        if not MISTRAL_API_KEY:
            raise ValueError(
                "MISTRAL_API_KEY not found in environment.\n"
                "Please set it in .env file: MISTRAL_API_KEY=your_key\n"
                "Get a free key at: https://console.mistral.ai"
            )
        
        return ChatMistralAI(
            model=MISTRAL_MODEL,
            api_key=MISTRAL_API_KEY,
            temperature=LLM_TEMPERATURE,
            max_tokens=LLM_MAX_TOKENS
        )
    
    elif LLM_PROVIDER == 'openai':
        if not OPENAI_API_KEY:
            raise ValueError(
                "OPENAI_API_KEY not found in environment.\n"
                "Please set it in .env file: OPENAI_API_KEY=your_key"
            )
        
        return ChatOpenAI(
            model=OPENAI_MODEL,
            api_key=OPENAI_API_KEY,
            temperature=LLM_TEMPERATURE,
            max_tokens=LLM_MAX_TOKENS
        )
    
    else:
        raise ValueError(
            f"Invalid LLM_PROVIDER: {LLM_PROVIDER}\n"
            f"Must be either 'mistral' or 'openai'"
        )


if __name__ == "__main__":
    # Test the LLM factory
    try:
        llm = get_llm()
        print(f"✓ LLM initialized: {LLM_PROVIDER}")
        print(f"✓ Model: {llm.model_name if hasattr(llm, 'model_name') else 'N/A'}")
        
        # Quick test
        response = llm.invoke("Say 'Hello from NeuroCare!'")
        print(f"✓ LLM responds: {response.content[:50]}...")
    except Exception as e:
        print(f"✗ Error initializing LLM: {e}")
        exit(1)
