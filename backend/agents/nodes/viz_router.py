
import logging
from backend.agents.state import AgentState

logger = logging.getLogger(__name__)

def viz_router_node(state: AgentState):
    """
    Decides if visualization is needed based on query results and user question.
    """
    logger.info("--- Viz Router Node ---")
    
    question = state.get("user_question", "").lower()
    query_results = state.get("query_result", [])
    
    # Simple Heuristics for now
    viz_keywords = ["chart", "plot", "graph", "visualize", "visualization", "trend", "distribution", "bar", "line", "pie"]
    
    explicit_request = any(k in question for k in viz_keywords)
    
    has_data = False
    is_table = False
    
    if query_results:
        result_text = query_results[0].get("result", "")
        # Check if it looks like a markdown table
        if "|" in result_text and "---" in result_text:
            is_table = True
            # Check row count (rough)
            lines = result_text.strip().split('\n')
            # Header + Separator + Data
            if len(lines) > 3: 
                has_data = True

    needs_viz = False
    
    if explicit_request and has_data:
        needs_viz = True
    elif has_data and ("over time" in question or "by month" in question or "compare" in question):
        needs_viz = True
        
    logger.info(f"Needs Visualization: {needs_viz}")
    
    return {
        "needs_visualization": needs_viz,
        "visualization_type": "plotly" if needs_viz else None
    }
