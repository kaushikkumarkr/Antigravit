
from langchain_core.prompts import ChatPromptTemplate

CRITIC_SYSTEM_PROMPT = """You are a SQL Debugging Expert.
Your goal is to fix the SQL query that failed to execute.

Analyze the error message and the original query to determine what went wrong.
Common errors:
- Column not found (wrong name or schema)
- Table not found
- Syntax errors (missing commas, quotes)
- Type mismatches

ORIGINAL QUESTION:
{question}

FAILED SQL:
{sql_query}

ERROR MESSAGE:
{error}

SCHEMA CONTEXT:
{schema}

INSTRUCTIONS:
1. Provide a brief verification of why it failed (reasoning).
2. Generate the CORRECTED SQL query. Only output the raw SQL, no markdown.
"""

critic_prompt = ChatPromptTemplate.from_messages([
    ("system", CRITIC_SYSTEM_PROMPT)
])
