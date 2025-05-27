import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import argparse
from tabulate import tabulate
from config.settings import DATABASE_URL

def get_db_connection():
    """Create a connection to the SQLite database."""
    # Extract the database path from the SQLAlchemy URL
    db_path = DATABASE_URL.replace('sqlite:///', '')
    return sqlite3.connect(db_path)

def get_table_names(conn):
    """Get list of all tables in the database."""
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    return [table[0] for table in cursor.fetchall()]

def get_table_info(conn, table_name):
    """Get column information for a specific table."""
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name});")
    return cursor.fetchall()

def get_recent_ticker_data(conn, limit=10, symbol=None):
    """Get recent ticker data with optional symbol filter."""
    query = """
    SELECT timestamp, symbol, last_price, volume_24h, turnover_24h, funding_rate
    FROM ticker_data
    """
    if symbol:
        query += f" WHERE symbol = '{symbol}'"
    query += " ORDER BY timestamp DESC LIMIT ?"
    
    return pd.read_sql_query(query, conn, params=(limit,))

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

def main():
    parser = argparse.ArgumentParser(description='Check Bybit database data')
    parser.add_argument('--tables', action='store_true', help='List all tables')
    parser.add_argument('--table-info', type=str, help='Show table structure')
    parser.add_argument('--recent', type=int, default=10, help='Show recent ticker data (default: 10)')
    parser.add_argument('--symbol', type=str, help='Filter by symbol (e.g., BTCUSDT)')
    parser.add_argument('--stats', action='store_true', help='Show ticker statistics')
    
    args = parser.parse_args()
    
    try:
        conn = get_db_connection()
        
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