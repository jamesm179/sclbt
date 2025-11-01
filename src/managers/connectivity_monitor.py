import logging
import platform
import subprocess
import threading
import time
from datetime import datetime
import requests
from src.config.config_manager import config_manager

class ConnectivityMonitor:
    def __init__(self, bot=None, notification_manager=None, telegram_notifier=None):
        self.bot = bot
        self.notification_manager = notification_manager
        self.telegram_notifier = telegram_notifier
        self.current_status = "Unknown"
        self.consecutive_failures = 0
        self.consecutive_successes = 0
        self.last_test_time = None
        self.last_ping_time = None
        self.monitoring_thread = None
        self.stop_monitoring_flag = threading.Event()
        self.status_lock = threading.Lock()
        self.ping_targets = ["8.8.8.8", "1.1.1.1"]
        self.http_targets = ["https://www.google.com", "https://api.binance.com"]
        self.ping_command = self._get_ping_command()
        self._initialize_connectivity_table()
        logging.info("ConnectivityMonitor initialized")

    def _get_ping_command(self):
        system = platform.system().lower()
        timeout_ms = config_manager.get('connectivity_ping_timeout', 2000)
        if system == "windows":
            return ["ping", "-n", "1", "-w", str(timeout_ms)]
        else:
            timeout_seconds = max(1, timeout_ms // 1000)
            return ["ping", "-c", "1", "-W", str(timeout_seconds)]

    def _initialize_connectivity_table(self):
        if not self.bot or not hasattr(self.bot, 'db_manager'):
            return
        # Placeholder for DB interaction
        logging.info("Connectivity monitoring database table would be initialized here.")

    def start_monitoring(self):
        if not config_manager.get('connectivity_monitoring_enabled', False):
            logging.info("Connectivity monitoring is disabled in config.")
            return
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            logging.warning("Connectivity monitoring is already running.")
            return
        self.stop_monitoring_flag.clear()
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        logging.info("Connectivity monitoring started.")

    def stop_monitoring(self):
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            self.stop_monitoring_flag.set()
            self.monitoring_thread.join(timeout=5)
            logging.info("Connectivity monitoring stopped.")

    def _monitoring_loop(self):
        while not self.stop_monitoring_flag.is_set():
            try:
                self._perform_connectivity_test()
                interval = 10 if self.current_status == "Lost" else config_manager.get('connectivity_test_interval', 60)
                self.stop_monitoring_flag.wait(interval)
            except Exception as e:
                logging.error(f"Error in connectivity monitoring loop: {e}")
                time.sleep(5)

    def _perform_connectivity_test(self):
        ping_result = self._test_ping()
        if ping_result['status'] == 'Success':
            self._analyze_test_results([ping_result])
        else:
            http_result = self._test_http()
            self._analyze_test_results([http_result])

    def _test_ping(self):
        for target in self.ping_targets:
            try:
                start_time = time.time()
                result = subprocess.run(self.ping_command + [target], capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    return {'method': 'ping', 'status': 'Success', 'response_time': int((time.time() - start_time) * 1000)}
            except Exception:
                continue
        return {'method': 'ping', 'status': 'Failed'}

    def _test_http(self):
        for target in self.http_targets:
            try:
                start_time = time.time()
                response = requests.get(target, timeout=config_manager.get('connectivity_http_timeout', 5))
                if response.status_code < 400:
                    return {'method': 'http', 'status': 'Success', 'response_time': int((time.time() - start_time) * 1000)}
            except Exception:
                continue
        return {'method': 'http', 'status': 'Failed'}

    def _analyze_test_results(self, test_results):
        successful_results = [r for r in test_results if r['status'] == 'Success']
        if successful_results:
            best_result = min(successful_results, key=lambda x: x.get('response_time', float('inf')))
            response_time = best_result.get('response_time')
            if response_time <= 100: new_status = "Normal"
            elif response_time <= 1000: new_status = "Slow"
            else: new_status = "Poor"
            self._update_status(new_status, response_time, f"Test via {best_result['method']}")
        else:
            self._update_status("Lost", None, "All connection tests failed")

    def _update_status(self, new_status, response_time, details):
        with self.status_lock:
            # Simplified status update logic
            if self.current_status != new_status:
                logging.info(f"Connectivity status changed: {self.current_status} -> {new_status} ({details})")
                self.current_status = new_status

    def set_bot(self, bot):
        self.bot = bot
        self._initialize_connectivity_table()
        if hasattr(bot, 'telegram_notifier'):
            self.telegram_notifier = bot.telegram_notifier
        if hasattr(bot, 'notification_manager'):
            self.notification_manager = bot.notification_manager
