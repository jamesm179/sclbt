import logging
from datetime import datetime

class EmergencyKillSwitch:
    """Emergency kill switch for immediate position closure"""

    def __init__(self, trading_engine, notification_manager=None):
        self.trading_engine = trading_engine
        self.notification_manager = notification_manager
        self.is_active = False
        self.trading_disabled = False
        self.execution_log = []

    def authenticate_password(self, password: str) -> bool:
        # This should be a more secure check in a real application
        return password == "admin123"

    async def execute_emergency_exit(self):
        try:
            self.is_active = True
            self.trading_disabled = True
            active_trades_copy = dict(self.trading_engine.active_trades)

            logging.warning(f"EMERGENCY KILL SWITCH ACTIVATED. Closing {len(active_trades_copy)} positions.")
            if self.notification_manager:
                await self.notification_manager.send_message(f"🚨 EMERGENCY KILL SWITCH ACTIVATED 🚨")

            closed_positions = []
            failed_positions = []

            for symbol, trade_data in active_trades_copy.items():
                try:
                    # In a real scenario, this would trigger an API call to the exchange
                    # Here, we simulate it by removing the trade from our internal state
                    del self.trading_engine.active_trades[symbol]
                    closed_positions.append(symbol)
                    logging.info(f"EMERGENCY EXIT: Closed position for {symbol}")
                except Exception as e:
                    failed_positions.append({'symbol': symbol, 'error': str(e)})
                    logging.error(f"EMERGENCY EXIT: Failed to close position for {symbol}: {e}")

            summary = f"Emergency exit complete. Closed: {len(closed_positions)}, Failed: {len(failed_positions)}."
            logging.info(summary)
            if self.notification_manager:
                await self.notification_manager.send_message(summary)

            return {'success': True, 'closed_positions': closed_positions, 'failed_positions': failed_positions}
        except Exception as e:
            logging.error(f"EMERGENCY KILL SWITCH: Critical error during execution: {e}")
            if self.notification_manager:
                await self.notification_manager.send_message(f"🚨 EMERGENCY EXIT ERROR: {e}")
            return {'success': False, 'error': str(e)}

    def re_enable_trading(self):
        self.trading_disabled = False
        self.is_active = False
        logging.info("EMERGENCY KILL SWITCH: Trading re-enabled.")
