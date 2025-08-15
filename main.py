import asyncio
import sys
import threading
import logging
import os
from src.core.bot import CryptoBot
from src.dashboard.app import DashboardApp

def setup_logging():
    # Ensure the logs directory exists
    os.makedirs("logs", exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[
            logging.FileHandler("logs/bot.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )

def main():
    setup_logging()

    # On Windows, a specific asyncio policy is needed for Dash to work with asyncio
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    try:
        # Initialize the bot
        bot = CryptoBot()

        # Initialize the dashboard with a reference to the bot
        dashboard = DashboardApp(bot)

        # Run the dashboard in a separate thread
        dash_thread = threading.Thread(target=dashboard.run, daemon=True)
        dash_thread.start()

        # Run the main async bot loop
        asyncio.run(bot.run())

    except KeyboardInterrupt:
        logging.info("Bot stopped by user.")
    except Exception as e:
        logging.critical(f"A fatal error occurred: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
