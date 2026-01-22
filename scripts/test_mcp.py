
import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.mcp.tools import handle_get_schema, handle_run_query, handle_get_sample_data

async def test_mcp_tools():
    print("🧪 Testing MCP Tools...")

    # 1. Test get_schema
    print("\n[1] Testing get_schema()...")
    result = await handle_get_schema()
    print("Schema Output (First 200 chars):")
    print(result[0].text[:200] + "...")
    assert "Table: customers" in result[0].text
    assert "column_name" not in result[0].text # Should verify formatted output not raw json

    # 2. Test run_query (Success)
    print("\n[2] Testing run_query (SELECT)...")
    result = await handle_run_query("SELECT COUNT(*) as count FROM customers")
    print("Query Output:")
    print(result[0].text)
    assert "count" in result[0].text
    assert "500" in result[0].text # Assuming 500 customers seeded

    # 3. Test run_query (Block DML)
    print("\n[3] Testing run_query (INSERT protection)...")
    result = await handle_run_query("INSERT INTO customers (name) VALUES ('Hacker')")
    print("Security Output:")
    print(result[0].text)
    assert "Security Violation" in result[0].text

    # 4. Test get_sample_data
    print("\n[4] Testing get_sample_data(products)...")
    result = await handle_get_sample_data("products", 3)
    print("Sample Data Output:")
    print(result[0].text)
    assert "category" in result[0].text
    
    # 5. Test get_sample_data (Non-existent table)
    print("\n[5] Testing get_sample_data(ghost_table)...")
    result = await handle_get_sample_data("ghost_table", 3)
    print("Error Output:")
    print(result[0].text)
    assert "does not exist" in result[0].text

    print("\n✅ All Manual Tests Passed!")

if __name__ == "__main__":
    try:
        asyncio.run(test_mcp_tools())
    except Exception as e:
        print(f"\n❌ Tests Failed: {e}")
        sys.exit(1)
