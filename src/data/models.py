from sqlalchemy import Column, Integer, String, Float, DateTime, BigInteger
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class OHLCV(Base):
    __tablename__ = 'ohlcv'

    id = Column(Integer, primary_key=True)
    exchange = Column(String, index=True)
    symbol = Column(String, index=True)
    timestamp = Column(BigInteger, index=True) # Store timestamp as integer for compatibility
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(Float)

    def __repr__(self):
        return (
            f"<OHLCV(exchange='{self.exchange}', symbol='{self.symbol}', "
            f"timestamp='{self.timestamp}', open={self.open}, high={self.high}, "
            f"low={self.low}, close={self.close}, volume={self.volume})>"
        )
