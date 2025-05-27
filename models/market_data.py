from datetime import datetime
from sqlalchemy import Column, Integer, Float, String, DateTime, JSON, Index, BigInteger
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


class TickerData(Base):
    __tablename__ = 'ticker_data'

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, index=True)
    symbol = Column(String(20), index=True)
    tick_direction = Column(String(20))
    price_24h_pcnt = Column(Float)
    last_price = Column(Float)
    prev_price_24h = Column(Float)
    high_price_24h = Column(Float)
    low_price_24h = Column(Float)
    prev_price_1h = Column(Float)
    mark_price = Column(Float)
    index_price = Column(Float)
    open_interest = Column(Float)
    open_interest_value = Column(Float)
    turnover_24h = Column(Float)
    volume_24h = Column(Float)
    next_funding_time = Column(BigInteger)
    funding_rate = Column(Float)
    bid1_price = Column(Float)
    bid1_size = Column(Float)
    ask1_price = Column(Float)
    ask1_size = Column(Float)
    pre_open_price = Column(String(50), nullable=True)
    pre_qty = Column(String(50), nullable=True)
    cur_pre_listing_phase = Column(String(50), nullable=True) 
    created_at = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return f"<TickerData(symbol='{self.symbol}', last_price={self.last_price})>" 