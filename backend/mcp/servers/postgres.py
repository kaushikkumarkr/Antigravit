
from mcp.server.fastmcp import FastMCP
import asyncpg
from typing import List, Dict, Any

class PostgresServer:
    def __init__(self, name: str, dsn: str):
        self.mcp = FastMCP(name)
        self.dsn = dsn
        self._register_tools()

    def _register_tools(self):
        @self.mcp.tool()
        async def query(sql: str) -> str:
            """Execute a read-only SQL query against the database."""
            if not sql.strip().upper().startswith("SELECT"):
                 return "Error: Only SELECT queries are allowed for safety."
            
            try:
                conn = await asyncpg.connect(self.dsn)
                try:
                    results = await conn.fetch(sql)
                    # Convert Record to dict and then JSON
                    import json
                    from datetime import date, datetime
                    from decimal import Decimal
                    
                    def json_serial(obj):
                        if isinstance(obj, (datetime, date)):
                            return obj.isoformat()
                        if isinstance(obj, Decimal):
                            return float(obj)
                        raise TypeError (f"Type {type(obj)} not serializable")
                        
                    data = [dict(r) for r in results]
                    return json.dumps(data, default=json_serial)
                finally:
                    await conn.close()
            except Exception as e:
                return f"Database Error: {e}"

        @self.mcp.tool()
        async def list_tables() -> List[str]:
            """List all public tables in the database."""
            try:
                conn = await asyncpg.connect(self.dsn)
                try:
                    query = "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
                    results = await conn.fetch(query)
                    return [r['table_name'] for r in results]
                finally:
                    await conn.close()
            except Exception as e:
                return []

        @self.mcp.tool()
        async def get_schema(table_name: str = None) -> str:
            """Get the schema definition for all tables or a specific table."""
            try:
                conn = await asyncpg.connect(self.dsn)
                try:
                    # Simple schema extraction query
                    # In a real app, this would be more robust (columns, types, fks)
                    # For now, let's just list columns for each table
                    
                    schema_text = ""
                    
                    # Get tables
                    tables_query = "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
                    if table_name:
                         tables_query += f" AND table_name = '{table_name}'"
                    
                    tables = await conn.fetch(tables_query)
                    
                    for table_record in tables:
                        t_name = table_record['table_name']
                        schema_text += f"\nTable: {t_name}\n"
                        
                        cols = await conn.fetch(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{t_name}'")
                        for col in cols:
                             schema_text += f"- {col['column_name']} ({col['data_type']})\n"
                    
                    return schema_text
                finally:
                    await conn.close()
            except Exception as e:
                return f"Error fetching schema: {e}"

    def run(self):
        # This is for running as a standalone process
        self.mcp.run()

if __name__ == "__main__":
    import os
    import logging
    
    # Configure logging
    logging.basicConfig(level=logging.ERROR)
    
    # Get DSN from environment
    # Default to the one in .env for testing, but typically passed by manager
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "5432")
    user = os.getenv("DB_USER", "postgres")
    password = os.getenv("DB_PASSWORD", "postgres_password")
    dbname = os.getenv("DB_NAME", "analytics_db")
    
    # Construct DSN
    dsn = f"postgresql://{user}:{password}@{host}:{port}/{dbname}"
    
    # Initialized database url if provided directly
    if os.getenv("DATABASE_URL"):
        dsn = os.getenv("DATABASE_URL")

    server = PostgresServer("postgres-mcp", dsn)
    server.run()
