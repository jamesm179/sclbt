class OHLCV:
    """
    A placeholder data model for OHLCV data.
    In a real application, this would likely be a SQLAlchemy model or similar.
    """
    def __init__(self, exchange, symbol, timestamp, open, high, low, close, volume):
        self.exchange = exchange
        self.symbol = symbol
        self.timestamp = timestamp
        self.open = open
        self.high = high
        self.low = low
        self.close = close
        self.volume = volume
