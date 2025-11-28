"""
Configuration loader utility
"""

import yaml
import os
from pathlib import Path
from typing import Dict, Any


def load_config(config_path: str = None) -> Dict[str, Any]:
    """
    Load configuration from YAML file
    
    Args:
        config_path: Path to config file (default: config/config.yaml)
        
    Returns:
        Configuration dictionary
    """
    if config_path is None:
        # Default config path
        config_path = Path(__file__).parent.parent.parent / "config" / "config.yaml"
    else:
        config_path = Path(config_path)
    
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Override with environment variables if present
    config = _apply_env_overrides(config)
    
    return config


def _apply_env_overrides(config: Dict[str, Any]) -> Dict[str, Any]:
    """Apply environment variable overrides to config"""
    
    # DATA_CSV override
    if 'DATA_CSV' in os.environ:
        config['data_csv'] = os.environ['DATA_CSV']
    
    # OPENAI_API_KEY for LLM calls
    if 'OPENAI_API_KEY' in os.environ:
        if 'api_keys' not in config:
            config['api_keys'] = {}
        config['api_keys']['openai'] = os.environ['OPENAI_API_KEY']
    
    return config
