import os
import sys

# A simple runner script for the trading bot.
# Runs the bot in test mode with default settings.

def run_bot():
    """
    Constructs and executes the command to run the main bot script
    with default parameters for easy testing.
    """
    print("--- Starting Trading Bot (Test Mode) ---")

    # Path to the python executable running this script
    python_executable = sys.executable

    command = [
        python_executable,
        "main.py",
        "--symbol", "BTC/USDT",
        "--timeframe", "1h",
        "--strategy", "rsi",
        "--test-mode"
    ]

    # Use a space to join command-parts for os.system
    command_str = " ".join(command)

    print(f"Executing command: {command_str}")

    try:
        os.system(command_str)
    except Exception as e:
        print(f"Failed to execute bot: {e}")

if __name__ == "__main__":
    run_bot()
