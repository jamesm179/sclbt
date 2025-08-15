from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.data.models import Base, OHLCV
from src.core.exceptions import DatabaseException
import pandas as pd

class DatabaseManager:
    def __init__(self, db_url):
        try:
            self.engine = create_engine(db_url)
            self.Session = sessionmaker(bind=self.engine)
        except Exception as e:
            raise DatabaseException(f"Failed to connect to database: {e}")

    def create_tables(self):
        try:
            Base.metadata.create_all(self.engine)
        except Exception as e:
            raise DatabaseException(f"Failed to create tables: {e}")

    def store_ohlcv(self, ohlcv_data: list[OHLCV]):
        session = self.Session()
        try:
            # A simple way to avoid duplicates: delete existing data for the same symbol/exchange/timestamp range
            if ohlcv_data:
                exchange = ohlcv_data[0].exchange
                symbol = ohlcv_data[0].symbol
                min_ts = min(o.timestamp for o in ohlcv_data)
                max_ts = max(o.timestamp for o in ohlcv_data)
                session.query(OHLCV).filter(
                    OHLCV.exchange == exchange,
                    OHLCV.symbol == symbol,
                    OHLCV.timestamp >= min_ts,
                    OHLCV.timestamp <= max_ts
                ).delete(synchronize_session=False)

            session.bulk_save_objects(ohlcv_data)
            session.commit()
        except Exception as e:
            session.rollback()
            raise DatabaseException(f"Failed to store OHLCV data: {e}")
        finally:
            session.close()

    def fetch_ohlcv_as_dataframe(self, exchange, symbol, since=None, limit=None, timeframe=None):
        session = self.Session()
        try:
            query = session.query(OHLCV).filter_by(exchange=exchange, symbol=symbol)

            if since:
                # 'since' can be a timestamp integer or datetime object
                if isinstance(since, pd.Timestamp):
                    since = int(since.timestamp() * 1000)
                query = query.filter(OHLCV.timestamp >= since)

            query = query.order_by(OHLCV.timestamp.asc())

            if limit:
                query = query.limit(limit)

            df = pd.read_sql(query.statement, session.bind)
            if not df.empty:
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                df.set_index('timestamp', inplace=True)

            return df
        except Exception as e:
            raise DatabaseException(f"Failed to fetch OHLCV data: {e}")
        finally:
            session.close()
