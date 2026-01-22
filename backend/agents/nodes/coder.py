
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
        raw_content = response.content.strip()
        
        # Extract SQL from markdown code blocks if present
        import re
        sql_match = re.search(r'```sql\s*(.*?)```', raw_content, re.DOTALL | re.IGNORECASE)
        if sql_match:
            sql_query = sql_match.group(1).strip()
        else:
            # Try generic code block
            code_match = re.search(r'```\s*(.*?)```', raw_content, re.DOTALL)
            if code_match:
                sql_query = code_match.group(1).strip()
                # Remove language hint if present (like "sql\n")
                if sql_query.lower().startswith("sql"):
                    sql_query = sql_query[3:].strip()
            else:
                # No code blocks, use raw content but check for common patterns
                # Sometimes LLM adds "SELECT" after explanation text
                select_match = re.search(r'(SELECT\s+.*)', raw_content, re.DOTALL | re.IGNORECASE)
                if select_match:
                    sql_query = select_match.group(1).strip()
                else:
                    sql_query = raw_content
        
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
