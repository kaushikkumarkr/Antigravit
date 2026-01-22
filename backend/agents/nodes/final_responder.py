
import logging
from backend.agents.state import AgentState
from backend.agents.llm import get_llm
from backend.agents.prompts.responder_prompt import responder_prompt

logger = logging.getLogger(__name__)

async def final_responder_node(state: AgentState):
    """
    Generates a natural language response based on the query result.
    """
    logger.info("--- Final Responder Node ---")
    
    user_question = state.get("user_question")
    sql_query = state.get("sql_query")
    query_result = state.get("query_result", [])
    
    # If result is too large, truncate it for the prompt
    result_str = str(query_result)
    if len(result_str) > 2000:
        result_str = result_str[:2000] + "... (truncated)"
        
    llm = get_llm(temperature=0.5)
    chain = responder_prompt | llm
    
    try:
        response = await chain.ainvoke({
            "user_question": user_question,
            "sql_query": sql_query,
            "query_result": result_str
        })
        
        return {
            "final_response": response.content
        }
    except Exception as e:
        logger.error(f"Final responder failed: {e}")
        return {
            "final_response": f"I found the data (Row count: {len(query_result)}), but couldn't generate a summary. Please check the visualization."
        }
