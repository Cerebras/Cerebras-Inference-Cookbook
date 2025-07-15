import yaml
import os

_config = None

def load_config():
    """Load configuration from config.yaml file."""
    global _config
    if _config is None:
        config_path = os.path.join(os.path.dirname(__file__), "config.yaml")
        try:
            with open(config_path, "r") as f:
                _config = yaml.safe_load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found at {config_path}")
        except yaml.YAMLError as e:
            raise ValueError(f"Error parsing YAML configuration: {e}")
    return _config

def get_config():
    """Get the loaded configuration."""
    return load_config()