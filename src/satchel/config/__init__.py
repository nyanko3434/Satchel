"""Loading and validating settings.

This package imports nothing else from Satchel. The command-line entry point
loads the settings and hands each part of the program what it needs.
"""

from satchel.config.errors import ConfigError
from satchel.config.loader import load_settings, read_api_key
from satchel.config.paths import Paths
from satchel.config.settings import ProviderSettings, ProviderType, Settings

__all__ = [
    "ConfigError",
    "Paths",
    "ProviderSettings",
    "ProviderType",
    "Settings",
    "load_settings",
    "read_api_key",
]
