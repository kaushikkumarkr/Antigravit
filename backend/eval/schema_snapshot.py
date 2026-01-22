"""
Schema Snapshot Utility

Generates a JSON snapshot of the current database schema for consistent evaluation.
This ensures tests run against a known schema even if the database evolves.
"""

import json
import asyncio
from datetime import datetime
from pathlib import Path

# Import the MCP manager to get schema from all sources
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.mcp.manager import MCPConnectionManager


async def generate_schema_snapshot() -> dict:
    """
    Fetches schema from all active MCP connections and returns a snapshot.
    """
    manager = MCPConnectionManager()
    
    snapshot = {
        "generated_at": datetime.now().isoformat(),
        "connections": [],
        "tables": {}
    }
    
    connections = manager.list_connections()
    
    for conn in connections:
        conn_info = {
            "id": conn["id"],
            "name": conn["name"],
            "type": conn["type"]
        }
        snapshot["connections"].append(conn_info)
        
        try:
            # Get schema for this connection
            schema = await manager.get_schema(conn["id"])
            
            # Parse tables from schema string
            if schema:
                snapshot["tables"][conn["id"]] = {
                    "raw_schema": schema[:2000] if len(schema) > 2000 else schema,
                    "connection_name": conn["name"]
                }
        except Exception as e:
            print(f"Warning: Could not get schema for {conn['name']}: {e}")
    
    return snapshot


def save_snapshot(snapshot: dict, output_path: str = None):
    """
    Saves the schema snapshot to a JSON file.
    """
    if output_path is None:
        output_path = Path(__file__).parent / "schema_snapshot.json"
    
    with open(output_path, "w") as f:
        json.dump(snapshot, f, indent=2)
    
    print(f"Schema snapshot saved to: {output_path}")
    return output_path


async def main():
    print("Generating schema snapshot...")
    snapshot = await generate_schema_snapshot()
    
    print(f"Found {len(snapshot['connections'])} connections")
    print(f"Captured schema for {len(snapshot['tables'])} sources")
    
    output_path = save_snapshot(snapshot)
    
    # Print summary
    print("\n--- Schema Snapshot Summary ---")
    for conn in snapshot["connections"]:
        print(f"  - {conn['name']} ({conn['type']})")
    
    return snapshot


if __name__ == "__main__":
    asyncio.run(main())
