"""
Faithfulness Judge

Uses an LLM to evaluate if a natural language response is faithfully grounded
in the provided data/SQL results (no hallucinations).
"""

import logging
from typing import Optional, List
from backend.agents.llm import get_llm

logger = logging.getLogger(__name__)

FAITHFULNESS_PROMPT = """You are evaluating an AI assistant's response for faithfulness to the data.

**User Question:**
{user_question}

**Data/SQL Result:**
{data_result}

**Assistant's Response:**
{assistant_response}

Evaluate if the assistant's response is FAITHFUL to the data provided:
1. Does the response accurately reflect the numbers/values in the data?
2. Are all claims in the response supported by the data?
3. Does the response avoid making up information not present in the data?

Respond with ONLY one of:
- FAITHFUL: The response accurately represents the data
- UNFAITHFUL: The response contains information not supported by the data
- PARTIAL: The response is mostly accurate but has minor unsupported claims

Your response (one word only):"""


async def judge_faithfulness(
    user_question: str,
    data_result: str,
    assistant_response: str
) -> dict:
    """
    Use an LLM to judge if the response is faithful to the data.
    
    Returns:
        dict with keys: verdict (str), reasoning (str)
    """
    if not assistant_response:
        return {
            "verdict": "SKIP",
            "reasoning": "No response to evaluate"
        }
    
    try:
        llm = get_llm(temperature=0.0)
        
        prompt = FAITHFULNESS_PROMPT.format(
            user_question=user_question,
            data_result=str(data_result)[:1000],  # Truncate long results
            assistant_response=assistant_response[:500]
        )
        
        response = await llm.ainvoke(prompt)
        verdict = response.content.strip().upper()
        
        # Normalize verdict
        if "FAITHFUL" in verdict and "UN" not in verdict:
            verdict = "FAITHFUL"
        elif "UNFAITHFUL" in verdict or "NOT" in verdict:
            verdict = "UNFAITHFUL"
        elif "PARTIAL" in verdict:
            verdict = "PARTIAL"
        else:
            verdict = "UNKNOWN"
        
        return {
            "verdict": verdict,
            "reasoning": response.content
        }
        
    except Exception as e:
        logger.error(f"Faithfulness Judge error: {e}")
        return {
            "verdict": "ERROR", 
            "reasoning": str(e)
        }


def is_faithful(verdict: str) -> bool:
    """Returns True if the response was judged as faithful."""
    return verdict in ["FAITHFUL", "PARTIAL"]
