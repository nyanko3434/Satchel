"""Command-line entry point.

This module only parses arguments and dispatches. It must stay thin: anything
that talks to a model, a knowledge base or a tool belongs behind the core.
"""

import argparse
import sys
from collections.abc import Sequence

from satchel import __version__


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
    subcommands = parser.add_subparsers(dest="command", metavar="<command>")
    subcommands.add_parser("chat", help="start a chat session (not implemented yet)")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "chat":
        print("satchel chat is not implemented yet (planned for v0).", file=sys.stderr)
        return 1

    parser.print_help()
    return 0
