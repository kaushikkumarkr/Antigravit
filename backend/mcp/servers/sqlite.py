
from mcp.server.fastmcp import FastMCP
import aiosqlite
import json
import os
from dateutil import parser

class SQLiteServer:
    def __init__(self, name: str, db_path: str):
        self.mcp = FastMCP(name)
        self.db_path = db_path
        self._register_tools()

    def _register_tools(self):
        @self.mcp.tool()
        async def query(sql: str) -> str:
            """Execute a read-only SQL query against the SQLite database."""
            if not sql.strip().upper().startswith("SELECT"):
                 return "Error: Only SELECT queries are allowed for safety."
            
            try:
                async with aiosqlite.connect(self.db_path) as db:
                    db.row_factory = aiosqlite.Row
                    async with db.execute(sql) as cursor:
                        rows = await cursor.fetchall()
                        # Convert Row objects to dicts
                        results = [dict(row) for row in rows]
                        return json.dumps(results)
            except Exception as e:
                return f"Database Error: {e}"

        @self.mcp.tool()
        async def list_tables() -> list[str]:
            """List all tables in the database."""
            try:
                async with aiosqlite.connect(self.db_path) as db:
                    async with db.execute("SELECT name FROM sqlite_master WHERE type='table';") as cursor:
                        rows = await cursor.fetchall()
                        return [row[0] for row in rows]
            except Exception as e:
                return []

        @self.mcp.tool()
        async def get_schema(table_name: str = None) -> str:
            """Get the schema definition (CREATE TABLE) for tables."""
            try:
                async with aiosqlite.connect(self.db_path) as db:
                    schema_text = ""
                    query = "SELECT name, sql FROM sqlite_master WHERE type='table'"
                    if table_name:
                        query += f" AND name='{table_name}'"
                    
                    async with db.execute(query) as cursor:
                        rows = await cursor.fetchall()
                        for row in rows:
                            schema_text += f"\nTable: {row[0]}\n"
                            schema_text += f"{row[1]}\n"
                    return schema_text
            except Exception as e:
                return f"Error fetching schema: {e}"

    def run(self):
        self.mcp.run()

if __name__ == "__main__":
    import os
    import logging
    
    logging.basicConfig(level=logging.ERROR)
    
    # Get DB Path from environment
    db_path = os.getenv("DB_PATH", "local.db")
    
    server = SQLiteServer("sqlite-mcp", db_path)
    server.run()
