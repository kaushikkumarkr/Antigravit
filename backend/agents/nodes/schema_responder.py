
import logging
from backend.agents.state import AgentState
from backend.mcp.tools import handle_get_schema

logger = logging.getLogger(__name__)

async def schema_responder_node(state: AgentState):
    """
    Answers questions about the database structure.
    """
    logger.info("--- Schema Responder Node ---")
    
    # Simple implementation: Return the full schema formatted nicely
    # Advanced: Use LLM to answer specific schema questions using the tool output
    
    schema_results = await handle_get_schema()
    schema_text = schema_results[0].text
    
    response = f"""Here is the current database schema:

{schema_text}
"""
    return {
        "final_response": response
    }
