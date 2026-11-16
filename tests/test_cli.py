import pytest

from satchel import __version__
from satchel.interface.cli import main


def test_version_flag_prints_version(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exit_info:
        main(["--version"])

    assert exit_info.value.code == 0
    assert capsys.readouterr().out.strip() == f"satchel {__version__}"


def test_no_command_prints_help(capsys: pytest.CaptureFixture[str]) -> None:
    assert main([]) == 0
    assert "usage: satchel" in capsys.readouterr().out


def test_chat_is_a_stub_for_now(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["chat"]) == 1
    assert "not implemented yet" in capsys.readouterr().err
