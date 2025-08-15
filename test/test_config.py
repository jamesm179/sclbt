import unittest
import os
from src.core.config import ConfigManager

class TestConfigManager(unittest.TestCase):

    def setUp(self):
        """Set up a test config file path and ensure env vars are clean."""
        self.config_path = 'test/test_config.yaml'
        # Store original env vars to restore them later, avoiding test pollution
        self.original_env = os.environ.copy()

    def tearDown(self):
        """Restore environment variables."""
        os.environ.clear()
        os.environ.update(self.original_env)

    def test_load_config(self):
        """Test that the config is loaded correctly."""
        cm = ConfigManager(config_path=self.config_path)
        self.assertIsNotNone(cm.config)
        self.assertEqual(cm.get('exchange.id'), 'test_exchange')

    def test_get_nested_value(self):
        """Test getting a nested value."""
        cm = ConfigManager(config_path=self.config_path)
        self.assertEqual(cm.get('strategies.rsi.rsi_period'), 10)

    def test_get_with_default(self):
        """Test getting a value with a default."""
        cm = ConfigManager(config_path=self.config_path)
        self.assertEqual(cm.get('non_existent.key', 'default_value'), 'default_value')

    def test_env_variable_override(self):
        """Test that environment variables override config values."""
        # Set environment variables for nested keys
        os.environ['EXCHANGE_ID'] = 'env_override_exchange'
        os.environ['STRATEGIES_RSI_RSI_PERIOD'] = '20' # Env vars are strings

        # We need to re-instantiate the manager to make it load the new env vars
        cm = ConfigManager(config_path=self.config_path)

        self.assertEqual(cm.get('exchange.id'), 'env_override_exchange')
        # The value from env var is a string, and our config manager casts it.
        self.assertEqual(cm.get('strategies.rsi.rsi_period'), 20)

    def test_config_file_not_found_no_exception(self):
        """Test that no exception is raised if config file is not found."""
        try:
            cm = ConfigManager(config_path='non_existent_config.yaml')
            # Should return default value
            self.assertEqual(cm.get('some.key', 'default'), 'default')
        except Exception as e:
            self.fail(f"ConfigManager raised an exception unexpectedly: {e}")

if __name__ == '__main__':
    unittest.main()
