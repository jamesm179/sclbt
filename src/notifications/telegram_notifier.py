import logging
import asyncio
from datetime import datetime
from telegram import Bot
from telegram.error import TelegramError
from .notification_manager import NotificationManager
from src.config.config_manager import config_manager

class TelegramNotifier:
    def __init__(self, display_manager=None):
        self.display = display_manager
        token = config_manager.get('telegram_token')
        self.chat_id = config_manager.get('telegram_chat_id')
        self.bot = Bot(token=token) if token and self.chat_id else None
        if not self.bot:
            logging.warning("Telegram token or chat_id not configured. Telegram notifications disabled.")
        self.last_signal_time = {}
        self.notification_manager = NotificationManager()

    async def send_message(self, text: str, parse_mode: str = "Markdown"):
        if not self.bot:
            return
        max_retries = 3
        retry_delay = 5
        for attempt in range(max_retries):
            try:
                await self.bot.send_message(
                    chat_id=self.chat_id,
                    text=text,
                    parse_mode=parse_mode,
                )
                return
            except TelegramError as e:
                logging.error(f"Telegram send error (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay)
            except Exception as e:
                logging.error(f"Unexpected Telegram send error: {e}")
                break

    async def send_signal(self, pair: str, signal_type: str, price: float, amount: float, balance: float, reason: str, direction: str, stop_loss_price: float, take_profit_price: float, profit_pct: float = None):
        current_time = datetime.now()
        pair_key = f"{pair}_{signal_type}"
        if pair_key in self.last_signal_time and (current_time - self.last_signal_time.get(pair_key, datetime.min)).seconds < 900:
            return # Debounce signals
        self.last_signal_time[pair_key] = current_time

        emoji = "🚀" if signal_type == "BUY" else "🛑" if signal_type == "SELL" else "ℹ️"
        message = (
            f"{emoji} *Sniper Bot V1 Signal (Paper Trade)* {emoji}\n"
            f"*Pair:* {pair}\n"
            f"*Action:* {signal_type} ({direction.upper()})\n"
            f"*Price:* {price:.4f}\n"
            f"*Amount:* {amount:.2f} USDT\n"
            f"*Stop Loss:* {stop_loss_price:.4f}\n"
            f"*Take Profit:* {take_profit_price:.4f}\n"
            f"*Balance:* {balance:.2f} USDT\n"
            f"*Reason:* {reason}\n"
            f"*Time:* {current_time.strftime('%Y-%m-%d %H:%M:%S')}"
        )
        if profit_pct is not None:
            message += f"\n*P/L:* {profit_pct:.2f}%"

        await self.send_message(message)

        if signal_type in ["BUY", "SELL"] and "P/L" not in reason:
            trade_direction = "long" if signal_type == "BUY" else "short"
            self.notification_manager.notify_trade(trade_direction, pair)
