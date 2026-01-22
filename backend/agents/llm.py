
import os
import logging
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from backend.config import settings

logger = logging.getLogger(__name__)

def get_llm(temperature: float = 0):
    """
    Returns the configured LLM client.
    Supports: ollama, lmstudio, google
    """
    provider = settings.LLM_PROVIDER.lower()
    logger.info(f"LLM Config - Provider: {provider}, Base URL: {settings.LLM_BASE_URL}, Model: {settings.LLM_MODEL_NAME}")
    
    try:
        if provider == "google":
            if not settings.GOOGLE_API_KEY:
                logger.warning("GOOGLE_API_KEY not set, falling back to local LLM")
            else:
                return ChatGoogleGenerativeAI(
                    model="gemini-1.5-pro", # Or make this configurable
                    google_api_key=settings.GOOGLE_API_KEY,
                    temperature=temperature,
                    convert_system_message_to_human=True
                )
        
        # Default to OpenAI compatible (Ollama, LM Studio, etc.)
        # Ollama uses http://localhost:11434/v1 as base URL
        return ChatOpenAI(
            base_url=settings.LLM_BASE_URL,
            api_key="ollama" if provider == "ollama" else "lm-studio",  # Dummy key for local servers
            model=settings.LLM_MODEL_NAME,
            temperature=temperature
        )
        
    except Exception as e:
        logger.error(f"Failed to initialize LLM: {e}")
        raise
