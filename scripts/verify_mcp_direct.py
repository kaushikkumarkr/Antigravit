
import asyncio
import os
import sqlite3
import json
from backend.mcp.manager import MCPConnectionManager

async def test_mcp_servers():
    print("--- Starting MCP Server Verification ---")
    manager = MCPConnectionManager()
    
    # 1. Test Postgres (Default)
    print("\n[1/3] Testing Postgres (Default)...")
    try:
        await manager.initialize_default_connection()
        # Simple query
        result = await manager.get_tool_result("default", "query", {"sql": "SELECT 1 as test"})
        print(f"✅ Postgres Result: {result.content[0].text}")
    except Exception as e:
        print(f"❌ Postgres Failed: {e}")

    # 2. Test SQLite
    print("\n[2/3] Testing SQLite...")
    # Create dummy db
    db_path = "test_verify.db"
    if os.path.exists(db_path):
        os.remove(db_path)
        
    conn = sqlite3.connect(db_path)
    conn.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)")
    conn.execute("INSERT INTO users (name) VALUES ('Alice')")
    conn.commit()
    conn.close()
    
    try:
        manager.add_connection({
            "id": "test-sqlite",
            "type": "sqlite",
            "name": "Test SQLite",
            "params": {"path": os.path.abspath(db_path)}
        })
        
        result = await manager.get_tool_result("test-sqlite", "query", {"sql": "SELECT * FROM users"})
        print(f"✅ SQLite Result: {result.content[0].text}")
    except Exception as e:
        print(f"❌ SQLite Failed: {e}")
    finally:
        if os.path.exists(db_path):
            os.remove(db_path)

    # 3. Test Filesystem
    print("\n[3/3] Testing Filesystem...")
    test_dir = "test_fs_sandbox"
    os.makedirs(test_dir, exist_ok=True)
    test_file = os.path.join(test_dir, "hello.txt")
    with open(test_file, "w") as f:
        f.write("Hello from MCP!")
        
    try:
        manager.add_connection({
            "id": "test-fs",
            "type": "filesystem",
            "name": "Test FS",
            "params": {"root_dir": os.path.abspath(test_dir)}
        })
        
        # Test 1: List Directory
        list_res = await manager.get_tool_result("test-fs", "list_directory", {"path": "."})
        print(f"✅ FS List Result: {list_res.content[0].text}") # FastMCP usually returns JSON string for complex types or list
        
        # Test 2: Read File
        read_res = await manager.get_tool_result("test-fs", "read_file", {"path": "hello.txt"})
        print(f"✅ FS Read Result: {read_res.content[0].text}")
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"❌ FS Failed: {e}")
    finally:
        import shutil
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)

    print("\n--- Verification Complete ---")

if __name__ == "__main__":
    asyncio.run(test_mcp_servers())
