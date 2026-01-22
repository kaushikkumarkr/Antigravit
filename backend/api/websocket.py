
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import logging
import json
from backend.agents.graph import graph
from langchain_core.messages import HumanMessage

logger = logging.getLogger(__name__)
router = APIRouter()

@router.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    logger.info("WebSocket endpoint called")
    await websocket.accept()
    logger.info("WebSocket accepted")
    
    try:
        while True:
            # Receive message (JSON with question)
            logger.info("Waiting for message...")
            data = await websocket.receive_text()
            logger.info(f"Raw data received: {data}")
            
            try:
                payload = json.loads(data)
                question = payload.get("question")
            except Exception as e:
                logger.error(f"JSON parse error: {e}")
                question = data # Fallback if raw string
            
            if not question:
                logger.warning("Empty question received")
                continue
                
            logger.info(f"Received question via WS: {question}")
            
            # Run Agent Graph with Streaming
            # We use astream to get events as nodes finish
            async for output in graph.astream({"user_question": question, "messages": [HumanMessage(content=question)]}):
                 for key, value in output.items():
                     # 'key' is the node name (e.g. 'router', 'architect')
                     # 'value' is the state update
                     
                     logger.info(f"Step completed: {key}")
                     
                     # Emit progress update
                     await websocket.send_json({
                         "type": "agent_update", 
                         "payload": {
                             "agent": key,
                             "status": "completed",
                             "message": f"{key.capitalize()} finished processing."
                         }
                     })
                     
                     # Perform final response check if output is from terminal nodes
                     # IMPORTANT: Only send final_response from actual terminal nodes, not intermediary ones
                     # visualizer -> final_responder flow means we should only respond at final_responder
                     terminal_nodes = ["error_handler", "schema_responder", "chat_responder", "clarifier", "final_responder"]
                     
                     if key in terminal_nodes:
                         logger.info(f"Processing final response for node: {key}")
                         
                         final_response_text = value.get("final_response")
                         visualization = None
                         
                         # Check for visualization_code in this node's output
                         if value.get("visualization_code"):
                             try:
                                 visualization = json.loads(value.get("visualization_code"))
                             except:
                                 pass
                         
                         # For final_responder, also check if it passed through visualization
                         # The visualizer sets visualization_code in state, final_responder should have it
                         if key == "final_responder" and not visualization:
                             # Try to get from the value if visualizer set it earlier
                             if value.get("visualization"):
                                 visualization = value.get("visualization")
                                  
                         response_payload = {
                             "answer": final_response_text or "Here is the response.",
                             "visualization": visualization
                         }
                         
                         logger.info(f"Sending final response payload: {response_payload}")
                         
                         await websocket.send_json({
                             "type": "final_response",
                             "payload": response_payload
                         })
                     
                     # Also handle Router/Executor specific text outputs if they acted as terminal in some paths?
                     # (Covered by terminal nodes above largely)

    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        try:
             await websocket.send_json({"type": "error", "payload": {"message": str(e)}})
        except:
            pass
