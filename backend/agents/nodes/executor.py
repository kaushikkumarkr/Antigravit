
import logging
from backend.agents.state import AgentState
from backend.mcp.tools import handle_run_query

logger = logging.getLogger(__name__)

async def executor_node(state: AgentState):
    """
    Executes the SQL query.
    """
    logger.info("--- Executor Node ---")
    
    sql_query = state.get("sql_query")
    if not sql_query:
        logger.error("No SQL query found in state")
        return {"sql_error": "No SQL generated"}
        
    try:
        # Execute query via MCP tool
        results = await handle_run_query(sql_query)
        
        # Parse TextContent result
        # handle_run_query returns list[TextContent]
        result_text = results[0].text
        
        # Check for error in text (simple heuristic based on our tool implementation)
        if "Error:" in result_text or "Security Violation:" in result_text or "Database Error:" in result_text:
             logger.error(f"Query execution failed: {result_text}")
             return {
                 "sql_error": result_text,
                 "final_response": f"I encountered an error executing the query: {result_text}"
             }
             
        logger.info("Query executed successfully")
        return {
            "query_result": [{"result": result_text}], # Storing raw text for now as the tool formats it as markdown
            "final_response": f"Here are the results:\n\n{result_text}"
        }
        
    except Exception as e:
        logger.error(f"Executor failed: {e}")
        return {"sql_error": str(e)}
