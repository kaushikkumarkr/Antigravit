
import logging
from backend.agents.state import AgentState
from backend.agents.llm import get_llm
from backend.agents.prompts.visualizer_prompt import visualizer_prompt

logger = logging.getLogger(__name__)

async def visualizer_node(state: AgentState):
    """
    Generates Plotly JSON for visualization.
    """
    logger.info("--- Visualizer Node ---")
    
    question = state.get("user_question")
    query_results = state.get("query_result", [])
    
    if not query_results:
        return {"visualization_code": None}
        
    data_context = query_results[0].get("result", "")
    
    llm = get_llm(temperature=0)
    chain = visualizer_prompt | llm
    
    try:
        response = await chain.ainvoke({
            "question": question,
            "data_context": data_context
        })
        
        json_code = response.content.strip()
        
        # Clean markdown
        if json_code.startswith("```json"):
            json_code = json_code[7:]
        if json_code.startswith("```"):
            json_code = json_code[3:]
        if json_code.endswith("```"):
            json_code = json_code[:-3]
        json_code = json_code.strip()
        
        logger.info("Generated Visualization Config")
        
        return {
            "visualization_code": json_code
        }
        
    except Exception as e:
        logger.error(f"Visualizer failed: {e}")
        return {"visualization_code": None}
