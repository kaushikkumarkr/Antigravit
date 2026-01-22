
import logging
from backend.agents.state import AgentState

logger = logging.getLogger(__name__)

def clarifier_node(state: AgentState):
    """
    Asks for clarification when intent is ambiguous.
    """
    logger.info("--- Clarifier Node ---")
    
    question = state.get("user_question", "")
    
    message = f"""I'm not quite sure I understood your request: "{question}"

Could you please rephrase it? 
- If you want to query data, try asking a specific question like "How many orders?"
- If you want to know about the database, ask "Show schema".
"""
    
    return {
        "final_response": message
    }
