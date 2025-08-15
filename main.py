import argparse
import logging
from src.bot.trading_bot import TradingBot
from src.core.exceptions import TradingBotException
import os
import shutil

def main():
    # Configure basic logging to capture logs from all modules
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        handlers=[
                            logging.FileHandler("logs/bot_run.log"),
                            logging.StreamHandler()
                        ])

    parser = argparse.ArgumentParser(description="Crypto Trading Bot")

    parser.add_argument('--symbol', required=True, help="Trading symbol, e.g., BTC/USDT")
    parser.add_argument('--timeframe', required=True, help="Timeframe, e.g., 1h, 4h, 1d")
    parser.add_argument('--strategy', required=True, help="Strategy to use, e.g., rsi")
    parser.add_argument('--config', default='config/config.yaml', help="Path to the configuration file")
    parser.add_argument('--test-mode', action='store_true', help="Enable test/sandbox mode")

    args = parser.parse_args()

    # Check if config file exists, if not, copy from example
    if not os.path.exists(args.config):
        example_config_path = 'config/config.example.yaml'
        if os.path.exists(example_config_path):
            print(f"Configuration file not found at {args.config}. Copying from {example_config_path}.")
            shutil.copy(example_config_path, args.config)
        else:
            print(f"ERROR: Default config {args.config} not found, and no example config available.")
            return

    try:
        bot = TradingBot(args)
        bot.run()
    except TradingBotException as e:
        print(f"ERROR: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
