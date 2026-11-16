"""The shape of the settings in ``config.toml``.

API keys are deliberately absent. A provider entry holds only the *name* of the
environment variable that carries its key, so a key can never leak through a
dump of these models or a trace. See ``read_api_key`` in ``loader``.
"""

from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from satchel.config.errors import ConfigError

# One value per adapter in the providers package.
ProviderType = Literal["anthropic", "openai_compat"]


class ProviderSettings(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    type: ProviderType
    model: str = Field(min_length=1)
    base_url: str | None = Field(default=None, min_length=1)
    api_key_env: str | None = Field(default=None, min_length=1)


class Settings(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    provider: str | None = None
    providers: dict[str, ProviderSettings] = Field(default_factory=dict)

    @model_validator(mode="after")
    def _provider_is_defined(self) -> Self:
        if self.provider is not None and self.provider not in self.providers:
            defined = ", ".join(sorted(self.providers)) or "none"
            raise ValueError(
                f"provider = {self.provider!r} does not match any "
                f"[providers.<name>] section (defined: {defined})"
            )
        return self

    def active_provider(self) -> tuple[str, ProviderSettings]:
        """The name and settings of the selected provider."""
        if not self.providers:
            raise ConfigError(
                "No provider is configured. Add a [providers.<name>] section to "
                'the config file and select it with provider = "<name>".'
            )
        if self.provider is None:
            defined = ", ".join(sorted(self.providers))
            raise ConfigError(
                'No provider is selected. Set provider = "<name>" in the config '
                f"file (defined: {defined})."
            )
        return self.provider, self.providers[self.provider]
