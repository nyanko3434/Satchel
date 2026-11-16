"""Where Satchel keeps its files, following the XDG Base Directory spec.

This module only computes paths. It never creates anything on disk; whoever
writes a file is responsible for creating its directory.
"""

from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Self

APP_NAME = "satchel"


def _xdg_dir(env: Mapping[str, str], variable: str, default: Path) -> Path:
    """The base directory named by an XDG variable, or the default.

    The spec says a value that is empty or not an absolute path must be ignored.
    """
    value = env.get(variable, "")
    if value and Path(value).is_absolute():
        return Path(value)
    return default


@dataclass(frozen=True, slots=True)
class Paths:
    config_dir: Path
    data_dir: Path
    state_dir: Path
    cache_dir: Path

    @classmethod
    def from_env(cls, env: Mapping[str, str], home: Path) -> Self:
        return cls(
            config_dir=_xdg_dir(env, "XDG_CONFIG_HOME", home / ".config") / APP_NAME,
            data_dir=_xdg_dir(env, "XDG_DATA_HOME", home / ".local" / "share")
            / APP_NAME,
            state_dir=_xdg_dir(env, "XDG_STATE_HOME", home / ".local" / "state")
            / APP_NAME,
            cache_dir=_xdg_dir(env, "XDG_CACHE_HOME", home / ".cache") / APP_NAME,
        )

    @property
    def config_file(self) -> Path:
        return self.config_dir / "config.toml"

    @property
    def recipes_file(self) -> Path:
        return self.config_dir / "recipes.toml"

    @property
    def kbs_dir(self) -> Path:
        return self.data_dir / "kbs"

    @property
    def traces_dir(self) -> Path:
        return self.state_dir / "traces"
