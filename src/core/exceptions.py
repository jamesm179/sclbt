class TradingBotException(Exception):
    """Base exception for the trading bot."""
    pass

class ConfigException(TradingBotException):
    """Exception raised for errors in the configuration."""
    pass

class APIConnectionException(TradingBotException):
    """Exception raised for errors related to API connection."""
    pass

class DatabaseException(TradingBotException):
    """Exception raised for errors related to the database."""
    pass

class StrategyException(TradingBotException):
    """Exception raised for errors within a strategy."""
    pass
