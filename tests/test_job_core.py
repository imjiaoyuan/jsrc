from datetime import datetime, timezone
from pathlib import Path

import pytest

from jsrc.job import core


class TestJobCoreHelpers:
    def test_to_int_valid(self):
        assert core.to_int("42") == 42
        assert core.to_int("0") == 0
        assert core.to_int("-1") == -1

    def test_to_int_invalid(self):
        assert core.to_int("not_a_number") == 0
        assert core.to_int("") == 0

    def test_to_float_valid(self):
        assert core.to_float("3.14") == 3.14
        assert core.to_float("0") == 0.0

    def test_to_float_invalid(self):
        assert core.to_float("") == 0.0


class TestJobCorePaths:
    def test_data_home_uses_xdg_when_set(self, monkeypatch):
        monkeypatch.setenv("XDG_DATA_HOME", "/custom/xdg")
        path = core.data_home()
        assert path == Path("/custom/xdg/jsrc")

    def test_data_home_default(self, monkeypatch):
        monkeypatch.delenv("XDG_DATA_HOME", raising=False)
        path = core.data_home()
        assert str(path).endswith(".local/share/jsrc")

    def test_history_path_uses_env_var(self, monkeypatch):
        monkeypatch.setenv("JSRC_JOBS_FILE", "/custom/path/jobs.tsv")
        assert core.history_path() == Path("/custom/path/jobs.tsv")

    def test_history_path_default(self, monkeypatch):
        monkeypatch.delenv("JSRC_JOBS_FILE", raising=False)
        monkeypatch.delenv("XDG_DATA_HOME", raising=False)
        path = core.history_path()
        assert path.name == "jobs"

    def test_state_dir(self, monkeypatch):
        monkeypatch.delenv("XDG_DATA_HOME", raising=False)
        assert core.state_dir().name == "job-state"

    def test_default_log_dir(self, monkeypatch):
        monkeypatch.delenv("XDG_DATA_HOME", raising=False)
        assert core.default_log_dir().name == "job-logs"


class TestJobCoreIO:
    def test_write_and_load_jobs_roundtrip(self, tmp_path, monkeypatch):
        monkeypatch.setenv("JSRC_JOBS_FILE", str(tmp_path / "jobs"))
        rows = [
            {"job_id": "1", "name": "test_job", "status": "running", "pid": "12345"},
            {"job_id": "2", "name": "other", "status": "exited", "pid": "67890"},
        ]
        for r in rows:
            for field in core.FIELDS:
                r.setdefault(field, "")
        core.write_jobs(rows)
        loaded = core.load_jobs()
        assert len(loaded) == 2
        assert loaded[0]["job_id"] == "1"
        assert loaded[1]["job_id"] == "2"

    def test_load_nonexistent_returns_empty(self, monkeypatch, tmp_path):
        monkeypatch.setenv("JSRC_JOBS_FILE", str(tmp_path / "nonexistent"))
        assert core.load_jobs() == []

    def test_write_with_keep_truncates(self, monkeypatch, tmp_path):
        monkeypatch.setenv("JSRC_JOBS_FILE", str(tmp_path / "jobs"))
        rows = [{k: str(i) for k in core.FIELDS} for i in range(10)]
        core.write_jobs(rows, keep=3)
        loaded = core.load_jobs()
        assert len(loaded) == 3

    def test_next_job_id_empty(self):
        assert core.next_job_id([]) == 1

    def test_next_job_id_increments(self):
        rows = [{"job_id": "5"}, {"job_id": "3"}]
        assert core.next_job_id(rows) == 6

    def test_state_file_read_and_write(self, tmp_path, monkeypatch):
        monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))
        core.state_dir().mkdir(parents=True)
        sf = core.state_file("42")
        sf.write_text("0\n", encoding="utf-8")
        assert core.read_exit_code("42") == "0"

    def test_read_exit_code_missing(self, tmp_path, monkeypatch):
        monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))
        assert core.read_exit_code("999") == ""

    def test_ensure_dirs_creates_directories(self, tmp_path, monkeypatch):
        monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))
        core.ensure_dirs()
        assert core.history_path().parent.exists()
        assert core.default_log_dir().exists()
        assert core.state_dir().exists()


class TestEtimeToSeconds:
    def test_empty_string(self):
        assert core.etime_to_seconds("") == 0

    def test_seconds_only(self):
        assert core.etime_to_seconds("45") == 45

    def test_mmss(self):
        assert core.etime_to_seconds("02:30") == 150

    def test_hhmmss(self):
        assert core.etime_to_seconds("01:15:30") == 4530

    def test_days(self):
        assert core.etime_to_seconds("2-10:00:00") == 2 * 86400 + 10 * 3600


class TestParseIso:
    def test_parse_valid(self):
        dt = core.parse_iso("2024-01-15T10:30:00")
        assert dt is not None
        assert dt.year == 2024
        assert dt.month == 1
        assert dt.hour == 10

    def test_parse_empty(self):
        assert core.parse_iso("") is None

    def test_parse_invalid(self):
        assert core.parse_iso("not_a_date") is None


class TestRuntimeSeconds:
    def test_running_uses_etime(self):
        row = {"status": "running"}
        live = {"etime": "01:30:00"}
        assert core.runtime_seconds(row, live) == 5400

    def test_stored_runtime(self):
        row = {"status": "exited", "runtime_sec": "3600"}
        assert core.runtime_seconds(row, {}) == 3600

    def test_from_start_end_times(self):
        row = {
            "status": "exited",
            "runtime_sec": "0",
            "start_time": "2024-01-15T10:00:00",
            "end_time": "2024-01-15T12:30:00",
        }
        assert core.runtime_seconds(row, {}) == 9000


class TestFormatDuration:
    def test_zero(self):
        assert core.format_duration(0) == "0s"

    def test_seconds(self):
        assert core.format_duration(45) == "45s"

    def test_minutes_seconds(self):
        assert core.format_duration(90) == "1m30s"

    def test_hours(self):
        assert core.format_duration(3661) == "1h01m01s"

    def test_days(self):
        assert core.format_duration(90061) == "1d01h01m01s"


class TestFilterRows:
    def test_empty_query_returns_all(self):
        rows = [
            {"command": "echo hello", "name": "", "log_path": ""},
            {"command": "bwa mem", "name": "", "log_path": ""},
        ]
        assert len(core.filter_rows(rows, "")) == 2

    def test_filter_matches_command(self):
        rows = [
            {"command": "echo hello", "name": "", "log_path": ""},
            {"command": "bwa mem ref.fa", "name": "", "log_path": ""},
        ]
        result = core.filter_rows(rows, "bwa")
        assert len(result) == 1
        assert result[0]["command"] == "bwa mem ref.fa"

    def test_filter_matches_name(self):
        rows = [
            {"command": "echo hi", "name": "my_job", "log_path": ""},
            {"command": "sleep 10", "name": "other", "log_path": ""},
        ]
        result = core.filter_rows(rows, "my_job")
        assert len(result) == 1

    def test_filter_case_insensitive(self):
        rows = [{"command": "BWA MEM", "name": "", "log_path": ""}]
        result = core.filter_rows(rows, "bwa")
        assert len(result) == 1


class TestSortRows:
    def test_sort_by_job_id(self):
        rows = [{"job_id": "3"}, {"job_id": "1"}, {"job_id": "2"}]
        result = core.sort_rows(rows, "job_id", reverse=False)
        assert [r["job_id"] for r in result] == ["1", "2", "3"]

    def test_sort_by_job_id_reverse(self):
        rows = [{"job_id": "1"}, {"job_id": "2"}, {"job_id": "3"}]
        result = core.sort_rows(rows, "job_id", reverse=True)
        assert [r["job_id"] for r in result] == ["3", "2", "1"]

    def test_sort_by_status(self):
        rows = [{"status": "running"}, {"status": "exited"}]
        result = core.sort_rows(rows, "status", reverse=False)
        assert result[0]["status"] == "exited"

    def test_sort_by_pid(self):
        rows = [{"pid": "100"}, {"pid": "50"}, {"pid": "200"}]
        result = core.sort_rows(rows, "pid", reverse=False)
        assert [r["pid"] for r in result] == ["50", "100", "200"]

    def test_sort_by_runtime(self):
        rows = [{"runtime_sec": "100"}, {"runtime_sec": "10"}]
        result = core.sort_rows(rows, "runtime_sec", reverse=False)
        assert result[0]["runtime_sec"] == "10"


class TestFindRow:
    def test_find_by_job_id(self):
        rows = [{"job_id": "1", "name": "a"}, {"job_id": "2", "name": "b"}]
        assert core.find_row(rows, "2")["name"] == "b"

    def test_find_by_pid_when_no_job_id_match(self):
        rows = [{"job_id": "10", "pid": "100"}, {"job_id": "20", "pid": "200"}]
        assert core.find_row(rows, "200")["job_id"] == "20"

    def test_find_by_name(self):
        rows = [{"job_id": "1", "name": "foo"}, {"job_id": "2", "name": "bar"}]
        assert core.find_row(rows, "foo")["job_id"] == "1"

    def test_find_not_found(self):
        assert core.find_row([], "nonexistent") is None

    def test_find_returns_latest_match(self):
        rows = [
            {"job_id": "1", "name": "foo"},
            {"job_id": "2", "name": "foo"},
            {"job_id": "3", "name": "foo"},
        ]
        assert core.find_row(rows, "foo")["job_id"] == "3"


class TestParseEnv:
    def test_valid(self):
        assert core.parse_env(["KEY=VAL", "FOO=bar"]) == {"KEY": "VAL", "FOO": "bar"}

    def test_no_equals_raises(self):
        with pytest.raises(SystemExit, match="invalid --env"):
            core.parse_env(["BADINPUT"])

    def test_empty_key_raises(self):
        with pytest.raises(SystemExit, match="invalid --env"):
            core.parse_env(["=val"])


class TestPrintRows:
    def test_print_table_empty(self, capsys):
        core.print_table([], ["job_id", "name"])
        out = capsys.readouterr().out
        assert "(no records)" in out

    def test_print_table_with_data(self, capsys):
        rows = [{"job_id": "1", "name": "test"}]
        core.print_table(rows, ["job_id", "name"])
        out = capsys.readouterr().out
        assert "1" in out
        assert "test" in out

    def test_print_rows_json(self, capsys):
        rows = [{"job_id": "1", "name": "test"}]
        core.print_rows(rows, ["job_id", "name"], fmt="json")
        out = capsys.readouterr().out
        import json

        data = json.loads(out)
        assert data[0]["job_id"] == "1"

    def test_print_rows_tsv(self, capsys):
        rows = [{"job_id": "1", "name": "test"}]
        core.print_rows(rows, ["job_id", "name"], fmt="tsv")
        out = capsys.readouterr().out
        assert out.startswith("job_id\tname")

    def test_print_rows_table_default(self, capsys):
        rows = [{"job_id": "1", "name": "test"}]
        core.print_rows(rows, ["job_id", "name"], fmt="table")
        out = capsys.readouterr().out
        assert "1" in out
        assert "test" in out


class TestTailLines:
    def test_tail_all(self, tmp_path):
        p = tmp_path / "log.txt"
        p.write_text("line1\nline2\nline3\n", encoding="utf-8")
        assert core.tail_lines(p, 0) == ["line1", "line2", "line3"]

    def test_tail_last_n(self, tmp_path):
        p = tmp_path / "log.txt"
        p.write_text("line1\nline2\nline3\nline4\nline5\n", encoding="utf-8")
        assert core.tail_lines(p, 2) == ["line4", "line5"]

    def test_tail_more_than_exists(self, tmp_path):
        p = tmp_path / "log.txt"
        p.write_text("a\nb\n", encoding="utf-8")
        assert core.tail_lines(p, 10) == ["a", "b"]

    def test_tail_with_trailing_newline(self, tmp_path):
        p = tmp_path / "log.txt"
        p.write_text("a\nb\n", encoding="utf-8")
        assert core.tail_lines(p, 1) == ["b"]


class TestToRowView:
    def test_basic_fields_preserved(self):
        row = {"job_id": "1", "name": "job1", "status": "running", "pid": "123"}
        live = {"etime": "00:05:00", "pcpu": "10.5", "stat": "R"}
        view = core.to_row_view(row, live)
        assert view["job_id"] == "1"
        assert view["status"] == "running"
        assert view["elapsed"] == "00:05:00"
        assert view["elapsed_sec"] == "300"
        assert view["runtime"] == "5m00s"
        assert view["cpu_pct"] == "10.5"

    def test_rss_calculations(self):
        row = {
            "rss_kb_last": "10240",
            "rss_kb_min": "8192",
            "rss_kb_peak": "20480",
            "rss_kb_sum": "61440",
            "rss_samples": "4",
        }
        view = core.to_row_view(row, {})
        assert view["rss_mb"] == "10.0"
        assert view["rss_min_mb"] == "8.0"
        assert view["rss_avg_mb"] == "15.0"
        assert view["rss_peak_mb"] == "20.0"

    def test_rss_min_defaults_to_last(self):
        row = {
            "rss_kb_last": "10240",
            "rss_kb_min": "0",
            "rss_kb_peak": "0",
            "rss_kb_sum": "0",
            "rss_samples": "0",
        }
        view = core.to_row_view(row, {})
        assert view["rss_min_mb"] == "10.0"

    def test_rss_avg_fallback_when_zero_samples(self):
        row = {
            "rss_kb_last": "10240",
            "rss_kb_min": "8192",
            "rss_kb_peak": "10240",
            "rss_kb_sum": "0",
            "rss_samples": "0",
        }
        view = core.to_row_view(row, {})
        assert view["rss_avg_mb"] == "10.0"


class TestRefreshJobs:
    def test_refresh_no_change_for_static_jobs(self):
        rows = [{"job_id": "1", "pid": "0", "status": "exited"}]
        result, changed = core.refresh_jobs(rows)
        assert not changed
        assert result[0]["status"] == "exited"
