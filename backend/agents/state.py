
import operator
from typing import TypedDict, List, Optional, Any, Annotated

class AgentState(TypedDict):
    """
    The state of the agent workflow, passed between nodes.
    """
    messages: Annotated[List[Any], operator.add]
    user_question: str
    intent: str
    intent_confidence: float
    schema_context: str
    relevant_tables: List[str]
    sql_query: str
    sql_error: Optional[str]
    retry_count: int
    query_result: List[dict]
    needs_visualization: bool
    visualization_type: Optional[str]
    visualization_code: str
    final_response: str
