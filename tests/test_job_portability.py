import logging
import subprocess

from jsrc.job import process


def test_process_alive_fallback_non_linux(monkeypatch):
    monkeypatch.setattr(process, "IS_LINUX", False)
    monkeypatch.setattr(process, "IS_WINDOWS", False)

    def _fake_kill(pid, sig):
        raise PermissionError

    monkeypatch.setattr(process.os, "kill", _fake_kill)
    assert process.process_alive(12345) is True


def test_ps_row_handles_missing_ps(monkeypatch):
    def _raise(*args, **kwargs):
        raise OSError

    monkeypatch.setattr(process.subprocess, "run", _raise)
    ok, etime, pcpu, stat = process.ps_row(123)
    assert ok is False
    assert etime == ""
    assert pcpu == 0.0
    assert stat == ""


def test_non_linux_rss_uses_ps(monkeypatch):
    monkeypatch.setattr(process, "IS_LINUX", False)

    def _fake_run(*args, **kwargs):
        return subprocess.CompletedProcess(args=args[0], returncode=0, stdout="456\n")

    monkeypatch.setattr(process.subprocess, "run", _fake_run)
    assert process.get_rss_kb_from_status(999) == 456


def test_portability_warning_only_once(monkeypatch, caplog):
    caplog.set_level(logging.WARNING)
    monkeypatch.setattr(process, "IS_LINUX", False)
    monkeypatch.setattr(process, "IS_MACOS", False)
    monkeypatch.setattr(process, "IS_WINDOWS", False)
    monkeypatch.setattr(process, "_PLATFORM_NOTE_EMITTED", False)
    process.warn_portability_limits()
    process.warn_portability_limits()
    assert caplog.text.count("non-Linux platform detected") == 1
