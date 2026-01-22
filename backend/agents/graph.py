
from langgraph.graph import StateGraph, END
from backend.agents.state import AgentState
from backend.agents.nodes.router import router_node
from backend.agents.nodes.architect import architect_node
from backend.agents.nodes.coder import coder_node
from backend.agents.nodes.executor import executor_node
from backend.agents.nodes.critic import critic_node
from backend.agents.nodes.error_handler import error_handler_node
from backend.agents.nodes.schema_responder import schema_responder_node
from backend.agents.nodes.chat_responder import chat_responder_node
from backend.agents.nodes.clarifier import clarifier_node
from backend.agents.nodes.viz_router import viz_router_node
from backend.agents.nodes.visualizer import visualizer_node
from backend.agents.nodes.final_responder import final_responder_node

# Define Graph
workflow = StateGraph(AgentState)

# Add Nodes
workflow.add_node("router", router_node)
workflow.add_node("architect", architect_node)
workflow.add_node("coder", coder_node)
workflow.add_node("executor", executor_node)
workflow.add_node("critic", critic_node)
workflow.add_node("error_handler", error_handler_node)
workflow.add_node("schema_responder", schema_responder_node)
workflow.add_node("chat_responder", chat_responder_node)
workflow.add_node("clarifier", clarifier_node)
workflow.add_node("viz_router", viz_router_node)
workflow.add_node("visualizer", visualizer_node)
workflow.add_node("final_responder", final_responder_node)

# Entry Point
workflow.set_entry_point("router")

# --- Routing Logic ---

def route_router(state: AgentState):
    intent = state.get("intent")
    confidence = state.get("intent_confidence", 0.0)
    
    # Low confidence -> Clarify
    if confidence < 0.7:
        return "clarifier"
        
    if intent == "DATA_QUERY":
        return "architect"
    elif intent == "SCHEMA_QUESTION":
        return "schema_responder"
    elif intent == "GENERAL_CHAT":
        return "chat_responder"
    else:
        return "clarifier" # Fallback

def route_executor(state: AgentState):
    sql_error = state.get("sql_error")
    retry_count = state.get("retry_count", 0)
    
    if sql_error:
        if retry_count < 3:
            return "critic"
        else:
            return "error_handler"
    else:
        # Success -> Go to Viz Router instead of END
        return "viz_router"

def route_viz_router(state: AgentState):
    if state.get("needs_visualization"):
        return "visualizer"
    else:
        return END

# --- Add Edges ---

workflow.add_conditional_edges(
    "router",
    route_router,
    {
        "architect": "architect",
        "schema_responder": "schema_responder",
        "chat_responder": "chat_responder",
        "clarifier": "clarifier"
    }
)

# Main Query Flow
workflow.add_edge("architect", "coder")
workflow.add_edge("coder", "executor")

# Execution & Retry Loop
workflow.add_conditional_edges(
    "executor",
    route_executor,
    {
        "critic": "critic",
        "error_handler": "error_handler",
        "viz_router": "viz_router"
    }
)

workflow.add_edge("critic", "executor")

# Output Layer
workflow.add_conditional_edges(
    "viz_router",
    route_viz_router,
    {
        "visualizer": "visualizer",
        END: "final_responder"
    }
)

workflow.add_edge("visualizer", "final_responder")
workflow.add_edge("final_responder", END)

# Terminal Nodes
workflow.add_edge("error_handler", END)
workflow.add_edge("schema_responder", END)
workflow.add_edge("chat_responder", END)
workflow.add_edge("clarifier", END)

# Compile
graph = workflow.compile()
