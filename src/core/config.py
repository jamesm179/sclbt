import yaml
import os
from dotenv import load_dotenv
from src.core.exceptions import ConfigException

class ConfigManager:
    def __init__(self, config_path='config/config.yaml'):
        load_dotenv()  # Load environment variables from .env file
        self.config_path = config_path
        self.config = self._load_config()

    def _load_config(self):
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
        except FileNotFoundError:
            # This is not an exception, we will just use defaults
            return {}
        except yaml.YAMLError as e:
            raise ConfigException(f"Error parsing YAML file: {e}")

        # Override with environment variables
        if config:
            self._override_with_env_vars(config)

        return config

    def _override_with_env_vars(self, config, prefix=''):
        for key, value in config.items():
            # Build the full environment variable name
            full_env_var_name = f"{prefix}{key}".upper()

            if isinstance(value, dict):
                # Recursively process the nested dictionary
                self._override_with_env_vars(value, prefix=f"{prefix}{key}_")
            else:
                env_value = os.getenv(full_env_var_name)
                if env_value is not None:
                    # Try to cast env var to the same type as the value in config
                    try:
                        # Handle boolean case specifically
                        if isinstance(value, bool):
                            config[key] = env_value.lower() in ('true', '1', 't')
                        else:
                            config[key] = type(value)(env_value)
                    except (ValueError, TypeError):
                        config[key] = env_value # Fallback to string

    def get(self, key, default=None):
        keys = key.split('.')
        value = self.config
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
