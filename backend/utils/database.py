
import os
import contextlib
import logging
from typing import Generator, Any
import psycopg2
from psycopg2.extensions import connection as _connection
from psycopg2.extras import RealDictCursor
from backend.config import settings

logger = logging.getLogger(__name__)

def get_db_connection() -> _connection:
    """
    Establish a connection to the PostgreSQL database.
    
    Returns:
        psycopg2 connection object
        
    Raises:
        psycopg2.Error: If connection fails
    """
    try:
        conn = psycopg2.connect(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            dbname=settings.DB_NAME,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD
        )
        return conn
    except psycopg2.Error as e:
        logger.error(f"Failed to connect to database: {e}")
        raise

@contextlib.contextmanager
def get_db_cursor(commit: bool = False) -> Generator[Any, None, None]:
    """
    Context manager for database cursor.
    Handles connection opening/closing and transaction commit/rollback.
    
    Args:
        commit: Whether to commit changes on success. Default False.
        
    Yields:
        psycopg2 cursor object (RealDictCursor)
    """
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            yield cur
            if commit:
                conn.commit()
    except Exception as e:
        if conn and commit:
            conn.rollback()
        logger.error(f"Database operation failed: {e}")
        raise
    finally:
        if conn:
            conn.close()
