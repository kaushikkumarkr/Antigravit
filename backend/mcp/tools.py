
import logging
from mcp.server import Server
from mcp.types import Tool, TextContent
from backend.utils.database import get_db_cursor
from backend.mcp.validator import validate_sql, SQLValidationError

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
    """
    Retrieves the database schema.
    If table_names is provided, returns schema only for those tables.
    Otherwise returns all public tables.
    """
    try:
        with get_db_cursor() as cur:
            # Base query
            query = """
                SELECT 
                    table_name, 
                    column_name, 
                    data_type, 
                    is_nullable
                FROM information_schema.columns 
                WHERE table_schema = 'public'
            """
            
            params = []
            if table_names:
                query += " AND table_name = ANY(%s)"
                params.append(table_names)
                
            query += " ORDER BY table_name, ordinal_position;"
            
            cur.execute(query, params)
            rows = cur.fetchall()
            
            if not rows:
                return [TextContent(type="text", text="No tables found matching criteria.")]
            
            # Group by table
            schema_output = []
            current_table = None
            
            for row in rows:
                table = row['table_name']
                if table != current_table:
                    if current_table:
                        schema_output.append("") # Spacer
                    schema_output.append(f"Table: {table}")
                    schema_output.append("-" * (len(table) + 7))
                    current_table = table
                
                col_info = f"- {row['column_name']} ({row['data_type']})"
                if row['is_nullable'] == 'YES':
                    col_info += " [NULLABLE]"
                schema_output.append(col_info)
                
            return [TextContent(type="text", text="\n".join(schema_output))]
            
    except Exception as e:
        logger.error(f"Error getting schema: {e}")
        return [TextContent(type="text", text=f"Error retrieving schema: {str(e)}")]


async def handle_run_query(sql: str) -> list[TextContent]:
    """
    Executes a read-only SQL query.
    Validates safety first.
    """
    try:
        # 1. Validate
        validate_sql(sql)
        
        # 2. Execute
        with get_db_cursor() as cur:
            cur.execute(sql)
            
            if cur.description is None:
                return [TextContent(type="text", text="Query executed successfully (No results returned).")]
                
            rows = cur.fetchall()
            
            if not rows:
                return [TextContent(type="text", text="No results found.")]
            
            # 3. Format Output (Markdown Table)
            # Get headers
            headers = [desc[0] for desc in cur.description]
            
            # Calculate widths
            widths = [len(h) for h in headers]
            data = []
            for row in rows:
                row_str = [str(val) for val in row.values()] # RealDictRow values
                data.append(row_str)
                for i, val in enumerate(row_str):
                    widths[i] = max(widths[i], len(val))
            
            # Build Table
            header_line = " | ".join(h.ljust(w) for h, w in zip(headers, widths))
            separator_line = "-|-".join("-" * w for w in widths)
            
            output = [header_line, separator_line]
            
            for row in data:
                 output.append(" | ".join(val.ljust(w) for val, w in zip(row, widths)))
                 
            return [TextContent(type="text", text="\n".join(output))]

    except SQLValidationError as e:
        return [TextContent(type="text", text=f"Security Violation: {str(e)}")]
    except Exception as e:
        logger.error(f"Query execution error: {e}")
        # Return sanitized error? For now, return string.
        return [TextContent(type="text", text=f"Database Error: {str(e)}")]


async def handle_get_sample_data(table_name: str, limit: int) -> list[TextContent]:
    """
    Helper to get sample data from a table safely.
    """
    # Sanitize limit
    limit = min(max(1, limit), 20)
    
    # Construct query (safe because table_name is parameterized? No, table names can't be parameterized directly easily in all drivers)
    # Better to validate table name exists in schema first.
    
    try:
        # Verify table exists to prevent injection via table_name
        with get_db_cursor() as cur:
            cur.execute("SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = %s", (table_name,))
            if not cur.fetchone():
                return [TextContent(type="text", text=f"Error: Table '{table_name}' does not exist.")]
                
            # Safe to run select *
            query = f"SELECT * FROM {table_name} LIMIT {limit}"
            
            # Reuse handle_run_query formatting!
            return await handle_run_query(query)
            
    except Exception as e:
         return [TextContent(type="text", text=f"Error retrieving sample data: {str(e)}")]
