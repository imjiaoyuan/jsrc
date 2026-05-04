import subprocess

from jsrc.job import commands


def test_process_alive_fallback_non_linux(monkeypatch):
    monkeypatch.setattr(commands, "IS_LINUX", False)

    def _fake_kill(pid, sig):
        raise PermissionError

    monkeypatch.setattr(commands.os, "kill", _fake_kill)
    assert commands._process_alive(12345) is True


def test_ps_row_handles_missing_ps(monkeypatch):
    def _raise(*args, **kwargs):
        raise OSError

    monkeypatch.setattr(commands.subprocess, "run", _raise)
    ok, etime, pcpu, stat = commands._ps_row(123)
    assert ok is False
    assert etime == ""
    assert pcpu == 0.0
    assert stat == ""


def test_non_linux_rss_uses_ps(monkeypatch):
    monkeypatch.setattr(commands, "IS_LINUX", False)

    def _fake_run(*args, **kwargs):
        return subprocess.CompletedProcess(args=args[0], returncode=0, stdout="456\n")

    monkeypatch.setattr(commands.subprocess, "run", _fake_run)
    assert commands._get_rss_kb_from_status(999) == 456


def test_portability_warning_only_once(monkeypatch, capsys):
    monkeypatch.setattr(commands, "IS_LINUX", False)
    monkeypatch.setattr(commands, "_PLATFORM_NOTE_EMITTED", False)
    commands._warn_portability_limits()
    commands._warn_portability_limits()
    err = capsys.readouterr().err
    assert err.count("non-Linux platform detected") == 1
