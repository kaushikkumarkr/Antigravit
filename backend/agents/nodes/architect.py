
import json
import logging
from backend.agents.state import AgentState
from backend.agents.llm import get_llm
from backend.agents.prompts.architect_prompt import architect_prompt
from backend.mcp.tools import handle_get_schema

logger = logging.getLogger(__name__)

async def architect_node(state: AgentState):
    """
    Identifies relevant tables for the query.
    """
    logger.info("--- Architect Node ---")
    
    question = state["user_question"]
    
    # 1. Get full schema
    # Using handle_get_schema directly since we are in the same process
    # In a real distributed system, this would be an MCP client call
    schema_results = await handle_get_schema()
    full_schema = schema_results[0].text
    
    # 2. Call LLM
    llm = get_llm(temperature=0)
    chain = architect_prompt | llm
    
    try:
        response = await chain.ainvoke({
            "schema": full_schema,
            "question": question
        })
        content = response.content
        
         # Strip markdown
        if "```json" in content:
            content = content.replace("```json", "").replace("```", "")
        elif "```" in content:
             content = content.replace("```", "")
             
        table_names = json.loads(content.strip())
        
        # Verify valid list
        if not isinstance(table_names, list):
             logger.warning("Architect didn't return a list, falling back to all")
             table_names = [] # Or all tables?
             
        logger.info(f"Identified tables: {table_names}")
        
        # 3. Get focused schema (optional optimization)
        # For now, we'll pass the full schema context or filter it?
        # Let's filter it to save tokens for the Coder
        if table_names:
            focused_schema_res = await handle_get_schema(table_names)
            schema_context = focused_schema_res[0].text
        else:
            schema_context = full_schema
            
        return {
            "relevant_tables": table_names,
            "schema_context": schema_context
        }
        
    except Exception as e:
        logger.error(f"Architect failed: {e}")
        # Fallback: pass full schema
        return {
            "relevant_tables": [],
            "schema_context": full_schema
        }
