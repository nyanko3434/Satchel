from pathlib import Path

import pytest

from satchel.config import Paths

HOME = Path("/home/someone")


def test_defaults_follow_the_xdg_spec() -> None:
    paths = Paths.from_env({}, HOME)

    assert paths.config_dir == HOME / ".config/satchel"
    assert paths.data_dir == HOME / ".local/share/satchel"
    assert paths.state_dir == HOME / ".local/state/satchel"
    assert paths.cache_dir == HOME / ".cache/satchel"


def test_derived_locations() -> None:
    paths = Paths.from_env({}, HOME)

    assert paths.config_file == HOME / ".config/satchel/config.toml"
    assert paths.recipes_file == HOME / ".config/satchel/recipes.toml"
    assert paths.kbs_dir == HOME / ".local/share/satchel/kbs"
    assert paths.traces_dir == HOME / ".local/state/satchel/traces"


@pytest.mark.parametrize(
    ("variable", "attribute"),
    [
        ("XDG_CONFIG_HOME", "config_dir"),
        ("XDG_DATA_HOME", "data_dir"),
        ("XDG_STATE_HOME", "state_dir"),
        ("XDG_CACHE_HOME", "cache_dir"),
    ],
)
def test_xdg_variables_override_the_defaults(variable: str, attribute: str) -> None:
    paths = Paths.from_env({variable: "/somewhere/else"}, HOME)

    assert getattr(paths, attribute) == Path("/somewhere/else/satchel")


@pytest.mark.parametrize("value", ["", "relative/dir", "./here"])
def test_empty_or_relative_xdg_values_are_ignored(value: str) -> None:
    paths = Paths.from_env({"XDG_CONFIG_HOME": value}, HOME)

    assert paths.config_dir == HOME / ".config/satchel"


def test_computing_paths_creates_nothing(tmp_path: Path) -> None:
    paths = Paths.from_env({}, tmp_path)

    assert paths.config_file.parent == tmp_path / ".config/satchel"
    assert list(tmp_path.iterdir()) == []
