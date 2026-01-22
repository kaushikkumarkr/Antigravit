
import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.agents.graph import graph

async def test_agent_flow():
    print("🤖 Testing Agent Workflow...")
    
    # 1. Test Data Query
    print("\n[Case 1] Simple Data Query: 'How many customers do we have?'")
    final_state = await graph.ainvoke({
        "user_question": "How many customers do we have?",
        "messages": []
    })
    
    print("\n--- Result Breakdown ---")
    print(f"Intent: {final_state.get('intent')}")
    print(f"Tables: {final_state.get('relevant_tables')}")
    print(f"SQL: {final_state.get('sql_query')}")
    print(f"Response: {final_state.get('final_response')}")
    
    if final_state.get("sql_query") and "SELECT" in final_state.get("sql_query"):
         print("✅ SQL generated successfully")
    else:
         print("❌ SQL generation failed")

    if "500" in str(final_state.get("final_response")):
         print("✅ Correct count returned")
    else:
         print("⚠️ Count verification specific to seed data might differ")

    # 2. Test General Chat (Should skip DB)
    print("\n[Case 2] General Chat: 'Hello there'")
    chat_state = await graph.ainvoke({
        "user_question": "Hello there",
        "messages": []
    })
    
    print(f"\nIntent: {chat_state.get('intent')}")
    # Based on our simple graph, if intent != DATA_QUERY, it ENDs immediately.
    # So relevant_tables/sql should be None.
    if not chat_state.get("relevant_tables"):
        print("✅ Correctly skipped Architect/Coder for chat")
    else:
        print("❌ Incorrectly routed to DB agents")

if __name__ == "__main__":
    try:
        asyncio.run(test_agent_flow())
    except Exception as e:
        print(f"\n❌ Test execution failed: {e}")
        # import traceback
        # traceback.print_exc()
