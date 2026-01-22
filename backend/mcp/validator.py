
import re
import logging

logger = logging.getLogger(__name__)

class SQLValidationError(Exception):
    pass

def validate_sql(sql: str) -> bool:
    """
    Validates that the SQL query is a safe READ-ONLY query.
    
    Rules:
    1. Must start with SELECT
    2. No INSERT, UPDATE, DELETE, DROP, TRUNCATE, ALTER, CREATE, GRANT, REVOKE
    3. No changes to system tables (pg_, information_schema)
    4. No multiple statements (semicolons) - basic check
    
    Args:
        sql: The SQL query string
        
    Returns:
        bool: True if valid, raises SQLValidationError if invalid
    """
    
    cleaned_sql = sql.strip()
    
    # Rule 4: prevent multiple statements (naive check, but effective for this scope)
    # allowing trailing semicolon
    if ';' in cleaned_sql[:-1]:
         raise SQLValidationError("Multiple statements are not allowed.")

    # Rule 1: Must start with SELECT
    if not re.match(r'^\s*SELECT', cleaned_sql, re.IGNORECASE):
        raise SQLValidationError("Only SELECT statements are allowed.")
        
    # Rule 2: Block DML/DDL keywords
    # Using word boundaries to avoid matching substrings (e.g., "update_at" column)
    forbidden_keywords = [
        r'\bINSERT\b', r'\bUPDATE\b', r'\bDELETE\b', r'\bDROP\b', 
        r'\bTRUNCATE\b', r'\bALTER\b', r'\bCREATE\b', r'\bGRANT\b', 
        r'\bREVOKE\b', r'\bEXEC\b', r'\bEXECUTE\b', r'\bUNION\b' # UNION might be okay, but locking down for now
    ]
    
    for keyword in forbidden_keywords:
        if re.search(keyword, cleaned_sql, re.IGNORECASE):
            clean_keyword = keyword.replace(r'\b', '')
            raise SQLValidationError(f"Forbidden keyword detected: {clean_keyword}")

    # Rule 3: Block System Tables
    if re.search(r'\bpg_', cleaned_sql, re.IGNORECASE) or \
       re.search(r'\binformation_schema\b', cleaned_sql, re.IGNORECASE):
        raise SQLValidationError("Access to system tables is not allowed.")
        
    return True
