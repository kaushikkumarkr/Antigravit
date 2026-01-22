
import logging
from backend.agents.state import AgentState
from backend.agents.llm import get_llm
from backend.agents.prompts.coder_prompt import coder_prompt
from backend.mcp.validator import validate_sql

logger = logging.getLogger(__name__)

async def coder_node(state: AgentState):
    """
    Generates SQL query.
    """
    logger.info("--- Coder Node ---")
    
    question = state["user_question"]
    schema = state["schema_context"]
    
    llm = get_llm(temperature=0)
    chain = coder_prompt | llm
    
    try:
        response = await chain.ainvoke({
            "schema": schema,
            "question": question
        })
        sql_query = response.content.strip()
        
        # Clean markdown
        if sql_query.startswith("```sql"):
            sql_query = sql_query[6:]
        if sql_query.startswith("```"):
            sql_query = sql_query[3:]
        if sql_query.endswith("```"):
            sql_query = sql_query[:-3]
            
        sql_query = sql_query.strip()
        
        # Validate (Agent level validation)
        # We also validate at MCP level, but catching early is good
        try:
             validate_sql(sql_query)
        except Exception as e:
            logger.error(f"Generated unsafe/invalid SQL: {e}")
            return {"sql_error": str(e), "sql_query": sql_query}
            
        logger.info(f"Generated SQL: {sql_query}")
        
        return {
            "sql_query": sql_query,
            "sql_error": None
        }
        
    except Exception as e:
        logger.error(f"Coder failed: {e}")
        return {"sql_error": str(e)}
