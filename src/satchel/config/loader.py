"""Reading ``config.toml`` and looking up API keys in the environment."""

import tomllib
from collections.abc import Mapping
from pathlib import Path

from pydantic import ValidationError

from satchel.config.errors import ConfigError
from satchel.config.settings import ProviderSettings, Settings


def load_settings(path: Path) -> Settings:
    """Load settings from a TOML file.

    A missing file is not an error: it gives empty settings, and the command
    that needs a provider reports that none is configured.
    """
    try:
        raw = path.read_bytes()
    except FileNotFoundError:
        return Settings()
    except OSError as error:
        raise ConfigError(f"{path}: cannot read file: {error.strerror}") from error

    try:
        data = tomllib.loads(raw.decode("utf-8"))
    except UnicodeDecodeError as error:
        raise ConfigError(f"{path}: file is not valid UTF-8") from error
    except tomllib.TOMLDecodeError as error:
        raise ConfigError(f"{path}: invalid TOML: {error}") from error

    try:
        return Settings.model_validate(data)
    except ValidationError as error:
        raise ConfigError(_describe(path, error)) from error


def _describe(path: Path, error: ValidationError) -> str:
    problems = []
    for item in error.errors():
        location = ".".join(str(part) for part in item["loc"])
        message = item["msg"].removeprefix("Value error, ")
        problems.append(f"{location}: {message}" if location else message)

    if len(problems) == 1:
        return f"{path}: {problems[0]}"
    listed = "\n".join(f"  - {problem}" for problem in problems)
    return f"{path}: {len(problems)} problems:\n{listed}"


def read_api_key(provider: ProviderSettings, env: Mapping[str, str]) -> str | None:
    """The provider's API key from the environment, or None if it needs no key."""
    if provider.api_key_env is None:
        return None

    key = env.get(provider.api_key_env, "")
    if not key:
        raise ConfigError(
            f"The environment variable {provider.api_key_env} is not set. "
            "It should hold the API key for this provider."
        )
    return key
