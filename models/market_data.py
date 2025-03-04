from datetime import datetime
from sqlalchemy import Column, Integer, Float, String, DateTime, JSON, Index
from sqlalchemy.sql import func
from db.database import Base

class Orderbook(Base):
    __tablename__ = "orderbooks"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True, nullable=False)
    timestamp = Column(DateTime, index=True, nullable=False)
    asks = Column(JSON)
    bids = Column(JSON)
    created_at = Column(DateTime, server_default=func.now())
    
    # Create composite index for faster queries
    __table_args__ = (
        Index('idx_orderbooks_symbol_timestamp', 'symbol', 'timestamp'),
    )

class Trade(Base):
    __tablename__ = "trades"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True, nullable=False)
    timestamp = Column(DateTime, index=True, nullable=False)
    trade_id = Column(String, index=True, nullable=False, unique=True)
    price = Column(Float, nullable=False)
    size = Column(Float, nullable=False)
    side = Column(String, nullable=False)  # 'Buy' or 'Sell'
    created_at = Column(DateTime, server_default=func.now())
    
    # Create composite index for faster queries
    __table_args__ = (
        Index('idx_trades_symbol_timestamp', 'symbol', 'timestamp'),
    )

class Kline(Base):
    __tablename__ = "klines"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True, nullable=False)
    interval = Column(String, index=True, nullable=False)
    start_time = Column(DateTime, index=True, nullable=False)
    open_price = Column(Float, nullable=False)
    high_price = Column(Float, nullable=False)
    low_price = Column(Float, nullable=False)
    close_price = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    
    # Create composite index for faster queries
    __table_args__ = (
        Index('idx_klines_symbol_interval_start_time', 'symbol', 'interval', 'start_time', unique=True),
    )