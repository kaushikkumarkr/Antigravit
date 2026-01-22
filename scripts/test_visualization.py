
import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.agents.graph import graph

async def test_visualization():
    print("📊 Testing Visualization Layer...")
    
    # 1. Test Explicit Visualization Request
    print("\n[Case 1] Explicit: 'Show me a bar chart of product stock by category'")
    # Note: "stock by category" implies aggregation. Coder should handle this.
    state_1 = await graph.ainvoke({
        "user_question": "Show me a bar chart of average product stock by category",
        "messages": []
    })
    
    print(f"SQL: {state_1.get('sql_query')}")
    print(f"Needs Viz: {state_1.get('needs_visualization')}")
    viz_code_1 = state_1.get('visualization_code')
    print(f"Viz Code (First 100 chars): {str(viz_code_1)[:100]}...")
    
    if viz_code_1 and '"data"' in viz_code_1 and '"layout"' in viz_code_1:
         print("✅ Plotly JSON generated successfully")
    else:
         print("❌ Visualization generation failed")
         
    # 2. Test No Visualization (Simple Count)
    print("\n[Case 2] No Viz: 'How many customers?'")
    state_2 = await graph.ainvoke({
        "user_question": "How many customers?",
        "messages": []
    })
    print(f"Needs Viz: {state_2.get('needs_visualization')}")
    if not state_2.get('needs_visualization'):
        print("✅ Correctly skipped visualization")
    else:
        print("❌ Incorrectly requested visualization")

if __name__ == "__main__":
    try:
        asyncio.run(test_visualization())
    except Exception as e:
        print(f"\n❌ Test execution failed: {e}")
