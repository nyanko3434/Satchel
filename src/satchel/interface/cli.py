"""Command-line entry point.

This module only parses arguments and dispatches. It must stay thin: anything
that talks to a model, a knowledge base or a tool belongs behind the core.
"""

import argparse
import os
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path

from satchel import __version__
from satchel.config import ConfigError, Paths, load_settings


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="satchel",
        description=(
            "A terminal assistant that answers from knowledge bases you control "
            "and carries out tasks on your machine, with your approval."
        ),
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )
    parser.add_argument(
        "--config",
        metavar="PATH",
        type=Path,
        help="config file to use (default: ~/.config/satchel/config.toml)",
    )
    subcommands = parser.add_subparsers(dest="command", metavar="<command>")
    subcommands.add_parser("chat", help="start a chat session (not implemented yet)")
    subcommands.add_parser(
        "config", help="show the loaded configuration and where Satchel keeps files"
    )
    return parser


def show_config(config_file: Path, paths: Paths, env: Mapping[str, str]) -> None:
    settings = load_settings(config_file)

    found = "found" if config_file.is_file() else "not found"
    print(f"Config file:  {config_file} ({found})")
    print(f"Provider:     {settings.provider or '(none selected)'}")
    print()

    if not settings.providers:
        print("Providers:    none configured")
    else:
        print("Providers:")
    for name, provider in settings.providers.items():
        active = " (active)" if name == settings.provider else ""
        print(f"  {name}{active}")
        print(f"    type:      {provider.type}")
        print(f"    model:     {provider.model}")
        if provider.base_url is not None:
            print(f"    base url:  {provider.base_url}")
        # Only ever report whether the variable is set, never its value.
        if provider.api_key_env is None:
            print("    api key:   not required")
        else:
            state = "set" if env.get(provider.api_key_env) else "not set"
            print(f"    api key:   ${provider.api_key_env} ({state})")
    print()

    print("Locations:")
    print(f"  data:    {paths.data_dir}")
    print(f"  state:   {paths.state_dir}")
    print(f"  cache:   {paths.cache_dir}")


def main(
    argv: Sequence[str] | None = None,
    *,
    env: Mapping[str, str] | None = None,
    home: Path | None = None,
) -> int:
    env = os.environ if env is None else env
    home = Path.home() if home is None else home

    parser = build_parser()
    args = parser.parse_args(argv)

    paths = Paths.from_env(env, home)
    config_file: Path = args.config if args.config is not None else paths.config_file

    try:
        if args.command == "chat":
            print(
                "satchel chat is not implemented yet (planned for v0).",
                file=sys.stderr,
            )
            return 1

        if args.command == "config":
            show_config(config_file, paths, env)
            return 0
    except ConfigError as error:
        print(f"satchel: {error}", file=sys.stderr)
        return 2

    parser.print_help()
    return 0
