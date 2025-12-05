"""
MySQL database connection and utilities
"""
import mysql.connector
from mysql.connector import pooling
from contextlib import contextmanager
from typing import Generator, Optional
from app.config import settings
import logging

logger = logging.getLogger(__name__)

# Connection pool for better performance
_connection_pool: Optional[pooling.MySQLConnectionPool] = None


def get_connection_pool() -> pooling.MySQLConnectionPool:
    """
    Get or create MySQL connection pool
    """
    global _connection_pool

    if _connection_pool is None:
        try:
            _connection_pool = pooling.MySQLConnectionPool(
                pool_name="kb_admin_pool",
                pool_size=10,
                pool_reset_session=True,
                host=settings.DB_HOST,
                port=settings.DB_PORT,
                user=settings.DB_USERNAME,
                password=settings.DB_PASSWORD,
                database=settings.DB_DATABASE,
                autocommit=False,
            )
            logger.info(f"MySQL connection pool created: {settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_DATABASE}")
        except mysql.connector.Error as e:
            logger.error(f"Failed to create connection pool: {e}")
            raise

    return _connection_pool


@contextmanager
def get_db_connection() -> Generator:
    """
    Context manager for database connections

    Usage:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM table")
    """
    pool = get_connection_pool()
    connection = None

    try:
        connection = pool.get_connection()
        yield connection
        connection.commit()
    except Exception as e:
        if connection:
            connection.rollback()
        logger.error(f"Database error: {e}")
        raise
    finally:
        if connection and connection.is_connected():
            connection.close()


def execute_query(query: str, params: tuple = None, fetch_one: bool = False, fetch_all: bool = False):
    """
    Execute a SQL query with error handling

    Args:
        query: SQL query string
        params: Query parameters (tuple)
        fetch_one: Return single result
        fetch_all: Return all results

    Returns:
        Query result or None
    """
    with get_db_connection() as conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params or ())

        if fetch_one:
            return cursor.fetchone()
        elif fetch_all:
            return cursor.fetchall()
        else:
            return cursor.lastrowid


def test_connection() -> bool:
    """
    Test database connection
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            return result[0] == 1
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        return False
