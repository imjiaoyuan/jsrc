from io import StringIO

from jsrc.core import progressbar, _fmt_duration


class TestFmtDuration:
    def test_seconds_only(self):
        assert _fmt_duration(45) == "00:45"

    def test_minutes_seconds(self):
        assert _fmt_duration(125) == "02:05"

    def test_hours_minutes_seconds(self):
        assert _fmt_duration(3661) == "1:01:01"

    def test_zero(self):
        assert _fmt_duration(0) == "00:00"


class TestProgressBar:
    def test_update_increments_count(self):
        bar = progressbar(total=10, tty_only=False)
        assert bar.n == 0
        bar.update(3)
        assert bar.n == 3
        bar.update()
        assert bar.n == 4

    def test_set_absolute_position(self):
        bar = progressbar(total=10, tty_only=False)
        bar.set(7)
        assert bar.n == 7

    def test_finish_sets_to_total(self):
        bar = progressbar(total=10, tty_only=False)
        bar.update(4)
        bar.finish()
        assert bar.n == 10
        assert bar._finished is True

    def test_finish_idempotent(self):
        bar = progressbar(total=10, tty_only=False)
        bar.finish()
        bar.finish()
        assert bar._finished is True

    def test_context_manager_finishes(self):
        with progressbar(total=5, tty_only=False) as bar:
            bar.update(3)
        assert bar.n == 5
        assert bar._finished is True

    def test_iter_known_length(self):
        items = [1, 2, 3, 4, 5]
        bar = progressbar(tty_only=False)
        result = list(bar.iter(items))
        assert result == [1, 2, 3, 4, 5]
        assert bar.total == 5
        assert bar.n == 5

    def test_iter_with_explicit_total(self):
        items = [1, 2, 3]
        bar = progressbar(tty_only=False)
        for _ in bar.iter(items, total=10):
            pass
        assert bar.total == 10

    def test_disabled_when_not_tty(self, monkeypatch):
        monkeypatch.setattr("sys.stderr", StringIO())

        bar = progressbar(total=10, tty_only=True)

        assert bar._enabled is False

    def test_render_does_not_raise(self, monkeypatch):
        monkeypatch.setattr("sys.stderr", StringIO())
        bar = progressbar(total=10, desc="Test", tty_only=False)
        bar._render(bar.start_time + 1.0)

    def test_render_complete_writes_newline(self, monkeypatch):
        stderr = StringIO()
        monkeypatch.setattr("sys.stderr", stderr)
        bar = progressbar(total=2, tty_only=False)
        bar.update(2)
        output = stderr.getvalue()
        assert "\n" in output

    def test_unknown_total_mode(self, monkeypatch):
        stderr = StringIO()
        monkeypatch.setattr("sys.stderr", stderr)
        bar = progressbar(total=0, desc="Count", tty_only=False)
        for _ in range(5):
            bar.update()
        bar.finish()
        output = stderr.getvalue()

        assert "5" in output
