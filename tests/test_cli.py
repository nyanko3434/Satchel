from pathlib import Path

import pytest

from satchel import __version__
from satchel.interface.cli import main

HOME = Path("/home/someone")

CONFIG = """\
provider = "groq"

[providers.claude]
type = "anthropic"
model = "some-claude-model"
api_key_env = "ANTHROPIC_API_KEY"

[providers.groq]
type = "openai_compat"
model = "some-groq-model"
base_url = "https://api.groq.com/openai/v1"
api_key_env = "GROQ_API_KEY"

[providers.local]
type = "openai_compat"
model = "some-local-model"
base_url = "http://localhost:11434/v1"
"""


def test_version_flag_prints_version(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exit_info:
        main(["--version"])

    assert exit_info.value.code == 0
    assert capsys.readouterr().out.strip() == f"satchel {__version__}"


def test_no_command_prints_help(capsys: pytest.CaptureFixture[str]) -> None:
    assert main([], env={}, home=HOME) == 0
    assert "usage: satchel" in capsys.readouterr().out


def test_chat_is_a_stub_for_now(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["chat"], env={}, home=HOME) == 1
    assert "not implemented yet" in capsys.readouterr().err


def test_config_shows_providers_and_locations(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    config_file = tmp_path / "config.toml"
    config_file.write_text(CONFIG, encoding="utf-8")
    env = {"GROQ_API_KEY": "secret-value"}

    assert main(["--config", str(config_file), "config"], env=env, home=HOME) == 0

    out = capsys.readouterr().out
    assert f"Config file:  {config_file} (found)" in out
    assert "Provider:     groq" in out
    assert "  groq (active)" in out
    assert "    model:     some-groq-model" in out
    assert "    base url:  https://api.groq.com/openai/v1" in out
    assert "    api key:   $GROQ_API_KEY (set)" in out
    assert "    api key:   $ANTHROPIC_API_KEY (not set)" in out
    assert "    api key:   not required" in out
    assert "  data:    /home/someone/.local/share/satchel" in out
    assert "  state:   /home/someone/.local/state/satchel" in out
    assert "  cache:   /home/someone/.cache/satchel" in out


def test_config_never_prints_the_key(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    config_file = tmp_path / "config.toml"
    config_file.write_text(CONFIG, encoding="utf-8")
    env = {"GROQ_API_KEY": "secret-value", "ANTHROPIC_API_KEY": "other-secret"}

    main(["--config", str(config_file), "config"], env=env, home=HOME)

    captured = capsys.readouterr()
    assert "secret" not in captured.out + captured.err


def test_config_without_a_file_uses_the_xdg_path(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert main(["config"], env={}, home=tmp_path) == 0

    out = capsys.readouterr().out
    assert f"Config file:  {tmp_path}/.config/satchel/config.toml (not found)" in out
    assert "Provider:     (none selected)" in out
    assert "Providers:    none configured" in out
    assert list(tmp_path.iterdir()) == []


def test_config_honours_xdg_config_home(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    config_dir = tmp_path / "xdg" / "satchel"
    config_dir.mkdir(parents=True)
    (config_dir / "config.toml").write_text(CONFIG, encoding="utf-8")
    env = {"XDG_CONFIG_HOME": str(tmp_path / "xdg")}

    assert main(["config"], env=env, home=HOME) == 0
    assert f"{config_dir}/config.toml (found)" in capsys.readouterr().out


def test_broken_config_is_one_clean_error(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    config_file = tmp_path / "config.toml"
    config_file.write_text(CONFIG.replace("provider =", "provder ="), encoding="utf-8")

    assert main(["--config", str(config_file), "config"], env={}, home=HOME) == 2

    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == (
        f"satchel: {config_file}: provder: Extra inputs are not permitted\n"
    )
