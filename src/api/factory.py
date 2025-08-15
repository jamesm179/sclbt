from .base_api import BaseExchangeAPI

class ExchangeAPIFactory:
    @staticmethod
    def create_api(exchange_name, credentials, display_manager, db_manager, config):
        # This will be expanded later to create specific exchange clients
        return BaseExchangeAPI(credentials, display_manager, db_manager, config)
