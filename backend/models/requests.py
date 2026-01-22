
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class QueryRequest(BaseModel):
    """
    Request model for the query endpoint.
    """
    question: str = Field(..., description="The natural language question to ask.")
    session_id: Optional[str] = Field(None, description="Optional session ID for conversation tracking.")
    options: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Optional configuration parameters.")

class SchemaRequest(BaseModel):
    """
    Request model for schema info (mostly for future use if we need to filter).
    """
    table_names: Optional[list[str]] = None

class ConnectionRequest(BaseModel):
    """
    Request model for managing MCP connections.
    """
    id: str = Field(..., description="Unique identifier for the connection.")
    type: str = Field(..., description="Type of connection: 'postgres', 'sqlite', 'filesystem'.")
    name: str = Field(..., description="Human-readable name.")
    params: Dict[str, Any] = Field(..., description="Connection parameters (host, port, etc).")

