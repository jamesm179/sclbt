import json
import os
import logging
import threading
import time
from typing import Dict, Any

class ConfigManager:
    def __init__(self, settings_file='bot_settings.json'):
        self.settings_file = settings_file
        self._config = {}
        self._lock = threading.Lock()
        self._last_mod_time = 0
        self.is_watching = False
        self.load_settings()

    def load_settings(self):
        try:
            with self._lock:
                if os.path.exists(self.settings_file):
                    self._last_mod_time = os.path.getmtime(self.settings_file)
                    with open(self.settings_file, 'r') as f:
                        self._config = json.load(f)
                    logging.info(f"Settings loaded from {self.settings_file}")
                else:
                    self._create_default_settings()
        except (json.JSONDecodeError, IOError) as e:
            logging.error(f"Error loading settings file: {e}. Using previous settings.")

    def save_settings(self):
        try:
            with self._lock:
                with open(self.settings_file, 'w') as f:
                    json.dump(self._config, f, indent=4)
                self._last_mod_time = os.path.getmtime(self.settings_file)
            logging.info(f"Settings saved to {self.settings_file}")
        except IOError as e:
            logging.error(f"Error saving settings file: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        with self._lock:
            return self._config.get(key, default)

    def set(self, key: str, value: Any):
        with self._lock:
            self._config[key] = value
        self.save_settings()

    def start_watching(self):
        if self.is_watching:
            return
        self.is_watching = True
        thread = threading.Thread(target=self._watch_file, daemon=True)
        thread.start()
        logging.info(f"Started watching {self.settings_file} for changes.")

    def _watch_file(self):
        while self.is_watching:
            try:
                if os.path.exists(self.settings_file):
                    mod_time = os.path.getmtime(self.settings_file)
                    if mod_time != self._last_mod_time:
                        logging.info(f"{self.settings_file} has been modified. Reloading settings.")
                        self.load_settings()
            except FileNotFoundError:
                # The file might have been deleted, just wait for it to reappear
                pass
            except Exception as e:
                logging.error(f"Error watching settings file: {e}")
            time.sleep(5) # Check every 5 seconds

    def _create_default_settings(self):
        # This method is called within a lock
        self._config = {
            "auto_trading": True, "leverage": 10, "active_strategies": ["main_strategy"],
            "colors": {"positive": "#00FF00", "negative": "#FF0000", "neutral": "#FFFFFF"},
            "strategies": {"main_strategy": {"ema50_period": 50, "ema200_period": 200}}
        }
        self.save_settings()

# Global instance
config_manager = ConfigManager()
