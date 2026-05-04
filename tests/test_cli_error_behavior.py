import sys

import pytest

from jsrc import cli


def test_cli_handles_missing_input_file(capsys, monkeypatch):
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "jsrc",
            "seq",
            "window",
            "-fa",
            "/tmp/does-not-exist.fa",
            "-w",
            "10",
            "-s",
            "2",
        ],
    )
    with pytest.raises(SystemExit) as exc:
        cli.main()
    assert exc.value.code == 2
    captured = capsys.readouterr()
    assert captured.err.startswith("Error: ")
