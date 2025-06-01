import sqlite3

import mysql.connector
import psycopg2

from config.settings import DATABASE_URL, DB_HOST, DB_NAME, DB_PASSWORD, DB_PORT, DB_TYPE, DB_USER


def get_db_connection():
    """
    Get a database connection based on DB_TYPE.
    Returns a connection object.
    """
    if DB_TYPE == "sqlite":
        db_path = DATABASE_URL.replace('sqlite:///', '')
        return sqlite3.connect(db_path)
    elif DB_TYPE == "postgresql":
        return psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
    elif DB_TYPE == "mysql":
        return mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
    else:
        raise ValueError(f"Unsupported database type: {DB_TYPE}")


def execute_query(query, params=None):
    """
    Execute a query and return results.
    Handles both SQLite and other database types.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        # For SELECT queries, fetch results
        if query.strip().upper().startswith('SELECT'):
            results = cursor.fetchall()
            return results
        else:
            conn.commit()
            return None
    finally:
        cursor.close()
        conn.close()


def check_db_connection():
    """
    Test database connection and return status.
    """
    try:
        conn = get_db_connection()
        conn.close()
        return True, f"Successfully connected to {DB_TYPE} database"
    except Exception as e:
        return False, f"Failed to connect to {DB_TYPE} database: {str(e)}"


def get_db_size():
    """
    Get database size based on database type.
    """
    if DB_TYPE == "sqlite":
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT page_count * page_size as size 
                FROM pragma_page_count(), pragma_page_size()
                """
            )
            return cursor.fetchone()[0]
        finally:
            conn.close()
    elif DB_TYPE == "postgresql":
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT pg_database_size(current_database())")
            return cursor.fetchone()[0]
        finally:
            conn.close()
    elif DB_TYPE == "mysql":
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT data_length + index_length 
                FROM information_schema.tables 
                WHERE table_schema = %s
            """, (DB_NAME,))
            return cursor.fetchone()[0]
        finally:
            conn.close()
    else:
        raise ValueError(f"Database size check not implemented for {DB_TYPE}")


if __name__ == "__main__":
    # Test the connection
    success, message = check_db_connection()
    print(message)
    
    if success:
        # Get database size
        size = get_db_size()
        print(f"Database size: {size} bytes") 