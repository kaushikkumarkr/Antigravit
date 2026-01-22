
import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.agents.graph import graph

async def test_intelligence():
    print("🧠 Testing Intelligence Features...")
    
    # 1. Test Schema Question (New Branch)
    print("\n[Case 1] Schema Question: 'What tables are in the database?'")
    state_1 = await graph.ainvoke({
        "user_question": "What tables are in the database?",
        "messages": []
    })
    print(f"Intent: {state_1.get('intent')}")
    print(f"Response: {state_1.get('final_response')[:100]}...") # Truncate
    if "customers" in state_1.get('final_response').lower():
        print("✅ Correctly identified schema question and returned tables")
        
    # 2. Test Ambiguous/Clarification (New Branch)
    print("\n[Case 2] Ambiguous Input: 'test'")
    state_2 = await graph.ainvoke({
        "user_question": "test",
        "messages": []
    })
    print(f"Intent: {state_2.get('intent')} (Confidence: {state_2.get('intent_confidence')})")
    print(f"Response: {state_2.get('final_response')}")
    if "rephrase" in state_2.get('final_response').lower():
        print("✅ Correctly asked for clarification")

    # 3. Test Self-Correction (Retry Loop)
    # We trick the agent by explicitly asking for a non-existent column to force an error
    print("\n[Case 3] Self-Correction: 'Get the phone number of customer 1'")
    # Note: 'phone_number' doesn't exist. 'email' is the contact info.
    # The architect might select 'customers'. The coder might guess 'phone' or 'phone_number'.
    # This should fail execution, trigger critic, and ideally be corrected to just 'name' or 'email' or fail gracefully.
    
    state_3 = await graph.ainvoke({
        "user_question": "Get the phone_number of customer id 1",
        "messages": []
    })
    
    print(f"Intent: {state_3.get('intent')}")
    print(f"Initial SQL: {state_3.get('sql_query')}")
    print(f"Error: {state_3.get('sql_error')}")
    print(f"Retry Count: {state_3.get('retry_count')}")
    
    # If retry_count > 0, it means Critic ran
    if state_3.get('retry_count') > 0:
        print("✅ Critic was triggered")
    else:
        print("⚠️ Critic was NOT triggered (maybe query succeeded immediately?)")
        
    print(f"Final Response: {state_3.get('final_response')}")

if __name__ == "__main__":
    try:
        asyncio.run(test_intelligence())
    except Exception as e:
        print(f"\n❌ Test execution failed: {e}")
