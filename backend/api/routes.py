
from fastapi import APIRouter, HTTPException
import logging
import json
from backend.models.requests import QueryRequest
from backend.models.responses import QueryResponse, SchemaResponse, HealthResponse
from backend.agents.graph import graph
from backend.mcp.tools import handle_get_schema
from langchain_core.messages import HumanMessage

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(
        components={
            "database": "connected", # Placeholder, ideally check actual DB
            "llm": "configured"
        }
    )

@router.get("/schema", response_model=SchemaResponse)
async def get_schema():
    try:
        results = await handle_get_schema()
        schema_text = results[0].text
        # Simple parsing for table names (could be better)
        lines = schema_text.split('\n')
        # Use set to remove duplicates if multiple connections have same table names
        tables = list(set(line.replace('Table: ', '').strip() for line in lines if line.startswith('Table: ')))
        tables.sort() # Sort for consistent display
        
        return SchemaResponse(schema_text=schema_text, tables=tables)
    except Exception as e:
        logger.error(f"Schema fetch failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/query", response_model=QueryResponse)
async def query_agent(request: QueryRequest):
    try:
        # Run graph synchronously (using ainvoke)
        final_state = await graph.ainvoke({
            "user_question": request.question,
            "messages": [HumanMessage(content=request.question)]
        })
        
        # Extract results
        answer = final_state.get("final_response", "I processed your request but have no text response.")
        sql_query = final_state.get("sql_query")
        intent = final_state.get("intent", "UNKNOWN")
        confidence = final_state.get("intent_confidence", 0.0)
        
        # Results (raw lists)
        results = final_state.get("query_result", [])
        
        # Visualization
        viz_code = final_state.get("visualization_code")
        visualization = None
        if viz_code:
            try:
                visualization = json.loads(viz_code)
            except:
                pass
                
        # If visualizer ran but didn't set a text response (it currently doesn't in our node impl),
        # provide a default one.
        if intent == "DATA_QUERY" and not answer and visualization:
            answer = "Here is the visualization for your data."
            
        return QueryResponse(
            answer=answer,
            sql_query=sql_query,
            results=None, # Converting raw TextContent to list of dicts is complex here without parsing the markdown table. Leaving as None for now.
            visualization=visualization,
            intent=intent,
            confidence=confidence,
            metadata={"step_count": pd_steps(final_state)}
        )
        
    except Exception as e:
        logger.error(f"Query failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def pd_steps(state):
    # Dummy step counter
    return 0

# --- Connection Management Endpoints ---

from backend.models.requests import ConnectionRequest
from backend.mcp.manager import manager

@router.get("/connections", response_model=list[ConnectionRequest])
async def list_connections():
    """List all configured connections."""
    return manager.list_connections()

@router.post("/connections", response_model=ConnectionRequest)
async def add_connection(request: ConnectionRequest):
    """Add a new connection."""
    try:
        manager.add_connection(request.dict())
        return request
    except Exception as e:
        logger.error(f"Failed to add connection: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/connections/{connection_id}")
async def remove_connection(connection_id: str):
    """Remove a connection."""
    try:
        manager.remove_connection(connection_id)
        return {"status": "success", "id": connection_id}
    except Exception as e:
        logger.error(f"Failed to remove connection: {e}")
        raise HTTPException(status_code=500, detail=str(e))
