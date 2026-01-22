
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class QueryResponse(BaseModel):
    """
    Response model for the query endpoint.
    """
    answer: str = Field(..., description="The natural language answer.")
    sql_query: Optional[str] = Field(None, description="The executed SQL query.")
    results: Optional[List[Dict[str, Any]]] = Field(None, description="The raw data results.")
    visualization: Optional[Dict[str, Any]] = Field(None, description="Plotly JSON configuration.")
    intent: str = Field(..., description="The classified intent.")
    confidence: float = Field(..., description="The intent confidence score.")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional execution info.")

class SchemaResponse(BaseModel):
    """
    Response model for schema information.
    """
    schema_text: str = Field(..., description="Text representation of the schema.")
    tables: List[str] = Field(..., description="List of table names.")

class HealthResponse(BaseModel):
    """
    Response model for health check.
    """
    status: str = "healthy"
    version: str = "0.1.0"
    components: Dict[str, str] = Field(default_factory=dict)
