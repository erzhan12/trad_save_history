# from datetime import datetime
from sqlalchemy import BigInteger, Column, DateTime, Float, Integer, String
from sqlalchemy.sql import func

from db.database import Base


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