
import logging
from langchain_core.messages import SystemMessage, HumanMessage
from backend.agents.state import AgentState
from backend.agents.llm import get_llm

logger = logging.getLogger(__name__)

CHAT_SYSTEM_PROMPT = """You are Antigravirt, a helpful data analysis assistant.
Your goal is to be friendly and helpful.
If the user asks who you are, explain that you are a local, privacy-first AI data analyst.
If the user asks what you can do, explain that you can query the local database to answer questions about customers, orders, and products.
Do not make up data.
"""

async def chat_responder_node(state: AgentState):
    """
    Handles general chat interactions.
    """
    logger.info("--- Chat Responder Node ---")
    
    question = state.get("user_question", "")
    llm = get_llm(temperature=0.7)
    
    messages = [
        SystemMessage(content=CHAT_SYSTEM_PROMPT),
        HumanMessage(content=question)
    ]
    
    logger.info("Invoking LLM for chat response...")
    try:
        response = await llm.ainvoke(messages)
        logger.info("LLM response received")
        return {
            "final_response": response.content
        }
    except Exception as e:
        import traceback
        logger.error(f"Chat Responder failed: {e}\n{traceback.format_exc()}")
        raise
