import json
import os
import logging
from typing import Dict, Any

class ConfigManager:
    def __init__(self, settings_file='bot_settings.json'):
        self.settings_file = settings_file
        self._config = {}
        self.load_settings()

    def load_settings(self):
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    self._config = json.load(f)
                logging.info(f"Settings loaded from {self.settings_file}")
            else:
                logging.warning(f"{self.settings_file} not found. Creating with default settings.")
                self._create_default_settings()
        except (json.JSONDecodeError, IOError) as e:
            logging.error(f"Error loading settings file: {e}. Recreating with defaults.")
            self._create_default_settings()

    def save_settings(self):
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self._config, f, indent=4)
            logging.info(f"Settings saved to {self.settings_file}")
        except IOError as e:
            logging.error(f"Error saving settings file: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        return self._config.get(key, default)

    def set(self, key: str, value: Any):
        self._config[key] = value
        self.save_settings()

    def get_all(self) -> Dict[str, Any]:
        return self._config.copy()

    def _create_default_settings(self):
        self._config = {
            "auto_trading": True,
            "auto_open_browser": True,
            "theme": "dark",
            "timeframe": "1h",
            "leverage": 10,
            "manual_trading_pairs": ["GALA/USDT", "RED/USDT"],
            "active_strategies": ["main_strategy", "trf_strategy"],
            "tp_sl_override_enabled": False,
            "override_take_profit": 15.0,
            "override_stop_loss": 7.0,
            "trailing_stop_enabled": True,
            "trailing_method": "percentage",
            "trailing_activation_profit": 20.0,
            "initial_trail_distance": 10.0,
            "trail_tightening_step": 6.0,
            "profit_increment_threshold": 10.0,
            "colors": {
                "positive": "#00FF00",
                "negative": "#FF0000",
                "neutral": "#FFFFFF"
            },
            "strategies": {
                "main_strategy": {
                    "ema50_period": 50, "ema200_period": 200, "cci1_length": 100,
                    "cci2_length": 40, "cci_long_level": 100, "cci_short_level": -100,
                    "use_long_signals": True, "use_short_signals": True, "use_cci1": True,
                    "use_cci2": True, "desired_take_profit": 7.0, "desired_stop_loss": 5.0
                },
                "rsi_cci_strategy": {
                    "rsi25_period": 25, "rsi100_period": 100, "cci40_period": 40,
                    "cci100_period": 100, "rsi_cross_level": 60, "cci40_cross_level": 200,
                    "cci100_cross_level": -45, "ema14_period": 14, "trail_percent": 12.0,
                    "use_long_signals": True, "use_short_signals": False
                },
                "trf_strategy": {
                    "per1": 27, "mult1": 2, "per2": 55, "mult2": 3,
                    "use_long_signals": True, "use_short_signals": True,
                    "desired_take_profit": 10.0, "desired_stop_loss": 5.0,
                    "cci_length": 100, "ema_length": 200, "cci_long_level": 100,
                    "cci_short_level": -100, "use_trending_signals": True, "use_reversal_signals": True
                }
            }
        }
        self.save_settings()

# Global instance
config_manager = ConfigManager()
