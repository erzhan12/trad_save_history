import argparse

import pandas as pd
from tabulate import tabulate

from utils.db_connect import get_db_connection


def get_table_names(conn):
    """Get list of all tables in the database."""
    cursor = conn.cursor()
    if conn.__class__.__name__ == 'SQLiteConnection':
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    else:
        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
    return [row[0] for row in cursor.fetchall()]


def get_table_info(conn, table_name):
    """Get column information for a specific table."""
    cursor = conn.cursor()
    if conn.__class__.__name__ == 'SQLiteConnection':
        cursor.execute(f"PRAGMA table_info({table_name});")
        return cursor.fetchall()
    else:
        cursor.execute("""
            SELECT 
                ordinal_position as cid,
                column_name as name,
                data_type as type,
                is_nullable = 'NO' as notnull,
                column_default as dflt_value,
                CASE WHEN is_identity = 'YES' THEN 1 ELSE 0 END as pk
            FROM information_schema.columns 
            WHERE table_name = %s
            ORDER BY ordinal_position;
        """, (table_name,))
        return cursor.fetchall()


def get_ticker_stats(conn, symbol=None):
    """Get statistics for ticker data."""
    query = """
    SELECT 
        symbol,
        COUNT(*) as record_count,
        MIN(timestamp) as first_record,
        MAX(timestamp) as last_record,
        AVG(last_price) as avg_price,
        MAX(last_price) as max_price,
        MIN(last_price) as min_price
    FROM ticker_data
    """
    if symbol:
        query += f" WHERE symbol = '{symbol}'"
    query += " GROUP BY symbol"
    
    return pd.read_sql_query(query, conn)


def get_recent_ticker_data(conn, limit=10, symbol=None):
    """Get recent ticker data."""
    query = """
    SELECT * FROM ticker_data
    """
    if symbol:
        query += f" WHERE symbol = '{symbol}'"
    query += f" ORDER BY timestamp DESC LIMIT {limit}"
    
    return pd.read_sql_query(query, conn)


def main():
    parser = argparse.ArgumentParser(description='Check Bybit database data')
    parser.add_argument('--tables', action='store_true', help='List all tables')
    parser.add_argument('--table-info', type=str, help='Show table structure')
    parser.add_argument('--recent', type=int, default=10, help='Show recent ticker data (default: 10)')
    parser.add_argument('--symbol', type=str, help='Filter by symbol (e.g., BTCUSDT)')
    parser.add_argument('--stats', action='store_true', help='Show ticker statistics')
    
    args = parser.parse_args()
    
    try:
        conn, _ = get_db_connection()
        
        if args.tables:
            tables = get_table_names(conn)
            print("\nAvailable tables:")
            for table in tables:
                print(f"- {table}")
                
        elif args.table_info:
            info = get_table_info(conn, args.table_info)
            print(f"\nTable structure for {args.table_info}:")
            print(tabulate(info, headers=['cid', 'name', 'type', 'notnull', 'dflt_value', 'pk']))
            
        elif args.stats:
            stats = get_ticker_stats(conn, args.symbol)
            print("\nTicker Statistics:")
            print(tabulate(stats, headers='keys', tablefmt='psql', showindex=False))
            
        else:
            data = get_recent_ticker_data(conn, args.recent, args.symbol)
            print("\nRecent Ticker Data:")
            print(tabulate(data, headers='keys', tablefmt='psql', showindex=False))
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'conn' in locals():
            conn.close()


if __name__ == "__main__":
    main() 