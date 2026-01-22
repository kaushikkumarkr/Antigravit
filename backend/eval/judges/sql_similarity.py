"""
SQL Similarity Judge

Uses an LLM to evaluate if two SQL queries are semantically equivalent.
This is useful for comparing generated SQL against reference SQL.
"""

import logging
from typing import Optional
from backend.agents.llm import get_llm

logger = logging.getLogger(__name__)

SQL_JUDGE_PROMPT = """You are an expert SQL analyst. Your task is to determine if two SQL queries are semantically equivalent - meaning they would return the same results when run against the same database.

**Reference SQL (Ground Truth):**
```sql
{reference_sql}
```

**Generated SQL (To Evaluate):**
```sql
{generated_sql}
```

Consider:
1. Do both queries target the same table(s)?
2. Do both queries select equivalent columns/aggregations?
3. Are WHERE clauses, GROUP BY, ORDER BY, and LIMIT functionally equivalent?
4. Minor syntax differences (e.g., alias names, whitespace) are acceptable.

Respond with ONLY one of:
- EQUIVALENT: The queries are semantically equivalent
- NOT_EQUIVALENT: The queries would return different results
- PARTIAL: The queries are similar but have meaningful differences

Your response (one word only):"""


async def judge_sql_similarity(
    reference_sql: str, 
    generated_sql: str
) -> dict:
    """
    Use an LLM to judge if generated SQL is semantically equivalent to reference.
    
    Returns:
        dict with keys: verdict (str), reasoning (str)
    """
    if not reference_sql or not generated_sql:
        return {
            "verdict": "SKIP",
            "reasoning": "Missing reference or generated SQL"
        }
    
    try:
        llm = get_llm(temperature=0.0)  # Deterministic for evaluation
        
        prompt = SQL_JUDGE_PROMPT.format(
            reference_sql=reference_sql.strip(),
            generated_sql=generated_sql.strip()
        )
        
        response = await llm.ainvoke(prompt)
        verdict = response.content.strip().upper()
        
        # Normalize verdict
        if "EQUIVALENT" in verdict and "NOT" not in verdict:
            verdict = "EQUIVALENT"
        elif "NOT" in verdict or "DIFFERENT" in verdict:
            verdict = "NOT_EQUIVALENT"
        elif "PARTIAL" in verdict:
            verdict = "PARTIAL"
        else:
            verdict = "UNKNOWN"
        
        return {
            "verdict": verdict,
            "reasoning": response.content
        }
        
    except Exception as e:
        logger.error(f"SQL Judge error: {e}")
        return {
            "verdict": "ERROR",
            "reasoning": str(e)
        }


# Convenience function for batch evaluation
def is_sql_equivalent(verdict: str) -> bool:
    """Returns True if the SQL was judged as equivalent."""
    return verdict in ["EQUIVALENT", "PARTIAL"]
