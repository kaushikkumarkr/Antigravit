
import json
import logging
from langchain_core.messages import HumanMessage
from backend.agents.state import AgentState
from backend.agents.llm import get_llm
from backend.agents.prompts.router_prompt import router_prompt

logger = logging.getLogger(__name__)

def router_node(state: AgentState):
    """
    Classifies the user's intent.
    """
    logger.info("--- Router Node ---")
    
    # Get the latest user message
    # Assuming the state is initialized with messages
    # If starting fresh, we might depend on user_question field if messages is empty
    user_input = state.get("user_question", "")
    if not user_input and state["messages"]:
         last_msg = state["messages"][-1]
         if isinstance(last_msg, HumanMessage) or hasattr(last_msg, 'content'):
             user_input = last_msg.content
         elif isinstance(last_msg, dict):
             user_input = last_msg.get('content', '')

    llm = get_llm(temperature=0)
    chain = router_prompt | llm
    
    try:
        # Add timeout to prevent hanging
        response = chain.invoke({"input": user_input}, config={"callbacks": [], "timeout": 10})
        content = response.content
        logger.info(f"Raw Router Response: {content}")
        
        # Strip markdown code blocks if present
        if "```json" in content:
            content = content.replace("```json", "").replace("```", "")
        elif "```" in content:
             content = content.replace("```", "")
             
        parsed = json.loads(content.strip())
        
        intent = parsed.get("intent", "AMBIGUOUS")
        confidence = parsed.get("confidence", 0.0)
        
        logger.info(f"Classified intent: {intent} ({confidence})")
        
        return {
            "intent": intent,
            "intent_confidence": confidence
        }
        
    except Exception as e:
        import traceback
        logger.error(f"Router failed: {e}\n{traceback.format_exc()}")
        # Fallback to general chat or ambiguous
        return {"intent": "GENERAL_CHAT", "intent_confidence": 0.0}
