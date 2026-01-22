
import logging
from backend.agents.state import AgentState
from backend.agents.llm import get_llm
from backend.agents.prompts.critic_prompt import critic_prompt
from backend.mcp.validator import validate_sql

logger = logging.getLogger(__name__)

async def critic_node(state: AgentState):
    """
    Analyzes and fixes failed SQL queries.
    """
    logger.info("--- Critic Node ---")
    
    question = state.get("user_question")
    sql_query = state.get("sql_query")
    error = state.get("sql_error")
    schema = state.get("schema_context", "")
    retry_count = state.get("retry_count", 0)
    
    llm = get_llm(temperature=0)
    chain = critic_prompt | llm
    
    try:
        logger.info(f"Attempting fix for error: {error}")
        
        response = await chain.ainvoke({
            "question": question,
            "sql_query": sql_query,
            "error": error,
            "schema": schema
        })
        
        new_sql = response.content.strip()
        
        # Clean markdown
        if new_sql.startswith("```sql"):
            new_sql = new_sql[6:]
        if new_sql.startswith("```"):
            new_sql = new_sql[3:]
        if new_sql.endswith("```"):
            new_sql = new_sql[:-3]
        new_sql = new_sql.strip()
        
        # Validate fixed SQL
        try:
             validate_sql(new_sql)
        except Exception as e:
            logger.error(f"Critic generated unsafe/invalid SQL: {e}")
            return {
                "sql_error": f"Critic failed to generate valid SQL: {e}",
                "retry_count": retry_count + 1
            }
            
        logger.info(f"Critic proposed fix: {new_sql}")
        
        return {
            "sql_query": new_sql,
            "sql_error": None, # Clear error to allow retry
            "retry_count": retry_count + 1
        }
        
    except Exception as e:
        logger.error(f"Critic failed: {e}")
        return {
            "retry_count": retry_count + 1
            # Keep error set so we exit loop
        }
