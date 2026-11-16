from pathlib import Path

import pytest

from satchel.config import (
    ConfigError,
    ProviderSettings,
    Settings,
    load_settings,
    read_api_key,
)

VALID = """\
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


def write(tmp_path: Path, text: str) -> Path:
    path = tmp_path / "config.toml"
    path.write_text(text, encoding="utf-8")
    return path


def test_missing_file_gives_empty_settings(tmp_path: Path) -> None:
    settings = load_settings(tmp_path / "does-not-exist.toml")

    assert settings == Settings()
    assert settings.provider is None
    assert settings.providers == {}


def test_valid_file_is_loaded(tmp_path: Path) -> None:
    settings = load_settings(write(tmp_path, VALID))

    assert settings.provider == "groq"
    assert list(settings.providers) == ["claude", "groq", "local"]
    assert settings.providers["claude"] == ProviderSettings(
        type="anthropic", model="some-claude-model", api_key_env="ANTHROPIC_API_KEY"
    )
    assert settings.providers["local"].api_key_env is None
    assert settings.providers["local"].base_url == "http://localhost:11434/v1"


def test_active_provider_returns_the_selected_entry(tmp_path: Path) -> None:
    name, provider = load_settings(write(tmp_path, VALID)).active_provider()

    assert name == "groq"
    assert provider.type == "openai_compat"
    assert provider.model == "some-groq-model"


def test_active_provider_with_nothing_configured() -> None:
    with pytest.raises(ConfigError, match="No provider is configured"):
        Settings().active_provider()


def test_active_provider_with_none_selected(tmp_path: Path) -> None:
    text = VALID.replace('provider = "groq"\n', "")
    settings = load_settings(write(tmp_path, text))

    with pytest.raises(ConfigError, match="No provider is selected") as error:
        settings.active_provider()
    assert "claude, groq, local" in str(error.value)


def test_invalid_toml_names_the_file(tmp_path: Path) -> None:
    path = write(tmp_path, "provider = \n")

    with pytest.raises(ConfigError, match="invalid TOML") as error:
        load_settings(path)
    assert str(path) in str(error.value)


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        pytest.param(
            VALID.replace("provider =", "provder ="),
            "provder: Extra inputs are not permitted",
            id="unknown-top-level-key",
        ),
        pytest.param(
            VALID.replace("base_url = ", "base_ur = ", 1),
            "providers.groq.base_ur: Extra inputs are not permitted",
            id="unknown-provider-key",
        ),
        pytest.param(
            VALID.replace('model = "some-groq-model"\n', ""),
            "providers.groq.model: Field required",
            id="missing-model",
        ),
        pytest.param(
            VALID.replace('"some-groq-model"', '""'),
            "providers.groq.model: String should have at least 1 character",
            id="empty-model",
        ),
        pytest.param(
            VALID.replace('"anthropic"', '"anthropc"'),
            "providers.claude.type: Input should be 'anthropic' or 'openai_compat'",
            id="unknown-type",
        ),
        pytest.param(
            VALID.replace('provider = "groq"', 'provider = "grok"'),
            "provider = 'grok' does not match any [providers.<name>] section "
            "(defined: claude, groq, local)",
            id="undefined-provider",
        ),
    ],
)
def test_invalid_settings_name_the_file_and_the_field(
    tmp_path: Path, text: str, expected: str
) -> None:
    path = write(tmp_path, text)

    with pytest.raises(ConfigError) as error:
        load_settings(path)
    assert str(error.value) == f"{path}: {expected}"


def test_several_problems_are_all_reported(tmp_path: Path) -> None:
    text = VALID.replace('"anthropic"', '"anthropc"').replace(
        'model = "some-groq-model"\n', ""
    )

    with pytest.raises(ConfigError) as error:
        load_settings(write(tmp_path, text))
    message = str(error.value)
    assert "2 problems:" in message
    assert "  - providers.claude.type: " in message
    assert "  - providers.groq.model: Field required" in message


def test_unreadable_path_is_a_config_error(tmp_path: Path) -> None:
    with pytest.raises(ConfigError, match="cannot read file"):
        load_settings(tmp_path)  # a directory, not a file


def test_file_that_is_not_utf8(tmp_path: Path) -> None:
    path = tmp_path / "config.toml"
    path.write_bytes(b"provider = \xff\xfe")

    with pytest.raises(ConfigError, match="not valid UTF-8"):
        load_settings(path)


def test_settings_cannot_be_changed_after_loading(tmp_path: Path) -> None:
    settings = load_settings(write(tmp_path, VALID))

    with pytest.raises(Exception, match="frozen"):
        settings.provider = "claude"  # type: ignore[misc]


GROQ = ProviderSettings(type="openai_compat", model="m", api_key_env="GROQ_API_KEY")
LOCAL = ProviderSettings(type="openai_compat", model="m")


def test_read_api_key_from_the_environment() -> None:
    assert read_api_key(GROQ, {"GROQ_API_KEY": "secret-value"}) == "secret-value"


def test_read_api_key_when_the_provider_needs_none() -> None:
    assert read_api_key(LOCAL, {"GROQ_API_KEY": "secret-value"}) is None


@pytest.mark.parametrize("env", [{}, {"GROQ_API_KEY": ""}])
def test_read_api_key_when_the_variable_is_missing(env: dict[str, str]) -> None:
    with pytest.raises(ConfigError, match="GROQ_API_KEY is not set"):
        read_api_key(GROQ, env)


def test_settings_never_contain_the_key(tmp_path: Path) -> None:
    settings = load_settings(write(tmp_path, VALID))

    assert "api_key" not in ProviderSettings.model_fields
    assert set(ProviderSettings.model_fields) == {
        "type",
        "model",
        "base_url",
        "api_key_env",
    }
    assert "secret" not in settings.model_dump_json()
