
import logging
import json
from mcp.server import Server
from mcp.types import Tool, TextContent
from backend.mcp.validator import validate_sql, SQLValidationError
from backend.mcp.manager import manager

logger = logging.getLogger(__name__)

def register_tools(server: Server):
    
    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return [
            Tool(
                name="get_schema",
                description="Get the database schema (tables and columns). Optional: provide 'table_names' list to filter.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "table_names": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Optional list of table names to get schema for"
                        }
                    }
                }
            ),
            Tool(
                name="run_query",
                description="Execute a read-only SQL query against the database.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "sql": {
                            "type": "string",
                            "description": "The SQL select statement to execute"
                        }
                    },
                    "required": ["sql"]
                }
            ),
             Tool(
                name="get_sample_data",
                description="Get sample rows from a specific table.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "table_name": {
                            "type": "string",
                            "description": "The name of the table"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Number of rows to return (default 5, max 20)",
                            "default": 5
                        }
                    },
                    "required": ["table_name"]
                }
            )
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[TextContent]:
        logger.info(f"Tool call: {name} with args: {arguments}")
        
        try:
            # Ensure connection is initialized
            await manager.initialize_default_connection()
            
            if name == "get_schema":
                return await handle_get_schema(arguments.get("table_names"))
            elif name == "run_query":
                return await handle_run_query(arguments.get("sql"))
            elif name == "get_sample_data":
                return await handle_get_sample_data(arguments.get("table_name"), arguments.get("limit", 5))
            else:
                raise ValueError(f"Unknown tool: {name}")
        except Exception as e:
            logger.error(f"Tool execution failed: {e}")
            return [TextContent(type="text", text=f"Error: {str(e)}")]

# Tool Implementations

async def handle_get_schema(table_names: list[str] = None) -> list[TextContent]:
    """Retrieves the database schema via MCP from ALL connections (with caching)."""
    try:
        combined_schema = ""
        connections = manager.list_connections()
        
        for conn in connections:
            conn_id = conn["id"]
            conn_name = conn.get("name", conn_id)
            
            try:
                # Check cache first
                cached = manager.get_cached_schema(conn_id)
                if cached:
                    text = cached
                else:
                    # Fetch from MCP and cache
                    mcp_result = await manager.get_tool_result(conn_id, "get_schema", {})
                    text = mcp_result.content[0].text
                    if text:
                        manager.set_cached_schema(conn_id, text)
                
                if text:
                    combined_schema += f"\n--- Connection: {conn_name} ---\n{text}\n"
            except Exception as e:
                logger.warning(f"Failed to fetch schema from {conn_id}: {e}")
                combined_schema += f"\n--- Connection: {conn_name} ---\n(Error fetching schema: {e})\n"
                
        if not combined_schema:
            combined_schema = "No tables found in any active connection."
            
        return [TextContent(type="text", text=combined_schema)]

    except Exception as e:
        logger.error(f"Error getting schema: {e}")
        return [TextContent(type="text", text=f"Error retrieving schema: {str(e)}")]


async def handle_run_query(sql: str) -> list[TextContent]:
    """Executes a read-only SQL query via MCP."""
    try:
        # 1. Validate
        validate_sql(sql)
        
        # 2. Execute via Manager
        mcp_result = await manager.get_tool_result("default", "query", {"sql": sql})
        
        # 3. Process Result
        raw_json_text = mcp_result.content[0].text
        
        if raw_json_text.startswith("Error") or raw_json_text.startswith("Database Error"):
             return [TextContent(type="text", text=raw_json_text)]
             
        rows = json.loads(raw_json_text)
        
        if not rows:
            return [TextContent(type="text", text="No results found.")]
            
        # 4. Format Output (Markdown Table)
        if len(rows) > 0:
            headers = list(rows[0].keys())
            widths = [len(h) for h in headers]
            data = []
            for row in rows:
                row_str = [str(row.get(h, '')) for h in headers]
                data.append(row_str)
                for i, val in enumerate(row_str):
                    widths[i] = max(widths[i], len(val))
            
            header_line = " | ".join(h.ljust(w) for h, w in zip(headers, widths))
            separator_line = "-|-".join("-" * w for w in widths)
            
            output = [header_line, separator_line]
            for row_data in data:
                 output.append(" | ".join(val.ljust(w) for val, w in zip(row_data, widths)))
                 
            return [TextContent(type="text", text="\n".join(output))]
        else:
             return [TextContent(type="text", text="Query executed successfully (No results returned).")]

    except SQLValidationError as e:
        return [TextContent(type="text", text=f"Security Violation: {str(e)}")]
    except Exception as e:
        logger.error(f"Query execution error: {e}")
        return [TextContent(type="text", text=f"Database Error: {str(e)}")]


async def handle_get_sample_data(table_name: str, limit: int) -> list[TextContent]:
    """Helper to get sample data via MCP."""
    limit = min(max(1, limit), 20)
    query = f"SELECT * FROM {table_name} LIMIT {limit}"
    return await handle_run_query(query)
