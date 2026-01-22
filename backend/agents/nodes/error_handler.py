
import logging
from backend.agents.state import AgentState

logger = logging.getLogger(__name__)

def error_handler_node(state: AgentState):
    """
    Handles terminal errors after retries are exhausted.
    """
    logger.info("--- Error Handler Node ---")
    
    error = state.get("sql_error", "Unknown error")
    question = state.get("user_question")
    
    # In a real system, we might use an LLM here to generate a polite apology based on the error
    # For now, a template message is sufficient and faster
    
    message = f"""I apologize, but I was unable to process your request after multiple attempts.

**Original Question:** {question}
**Error Encountered:** {error}

Please try rephrasing your question or checking if the data you are looking for exists in the database.
"""
    
    return {
        "final_response": message
    }
