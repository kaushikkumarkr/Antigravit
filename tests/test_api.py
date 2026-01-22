
from fastapi.testclient import TestClient
from backend.main import app
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

client = TestClient(app)

def test_health():
    print("\n🏥 Testing Health Endpoint...")
    response = client.get("/api/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    print("✅ Health Check Passed")

def test_schema():
    print("\n📄 Testing Schema Endpoint...")
    response = client.get("/api/schema")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Tables: {data.get('tables')}")
    assert response.status_code == 200
    assert "customers" in data["tables"]
    print("✅ Schema Check Passed")

def test_query():
    print("\n🤖 Testing Query Endpoint...")
    payload = {"question": "How many customers do we have?"}
    response = client.post("/api/query", json=payload)
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Answer: {data.get('answer')}")
    print(f"Intent: {data.get('intent')}")
    assert response.status_code == 200
    assert data["intent"] == "DATA_QUERY"
    print("✅ Query Check Passed")

def test_websocket():
    print("\n🔌 Testing WebSocket...")
    with client.websocket_connect("/ws/chat") as websocket:
        websocket.send_json({"question": "Hello"})
        
        # We expect multiple messages
        # 1. updates...
        # 2. final response
        
        responses = []
        try:
            while True:
                # Set a timeout or count
                data = websocket.receive_json()
                responses.append(data)
                print(f"Received: {data['type']}")
                if data['type'] == 'final_response':
                    break
        except Exception as e:
            print(f"WS Loop ended: {e}")
            
        assert len(responses) > 0
        final = responses[-1]
        assert final["type"] == "final_response"
        print("✅ WebSocket Check Passed")

if __name__ == "__main__":
    try:
        test_health()
        test_schema()
        test_query()
        test_websocket()
        print("\n🎉 ALL API TESTS PASSED!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        # import traceback
        # traceback.print_exc()
