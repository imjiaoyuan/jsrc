import sys
import time
from typing import Any
from collections.abc import Generator, Iterable


def _fmt_duration(seconds: float) -> str:
    t = int(seconds)
    h, m, s = t // 3600, (t % 3600) // 60, t % 60
    if h:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"


class progressbar:
    def __init__(
        self,
        total: int = 0,
        desc: str = "",
        width: int = 40,
        min_interval: float = 0.1,
        tty_only: bool = True,
    ):
        self.total = total
        self.desc = desc
        self.width = width
        self.min_interval = min_interval
        self.n = 0
        self.start_time = time.time()
        self._last_update = 0.0
        self._finished = False
        self._enabled = not tty_only or sys.stderr.isatty()

    def update(self, n: int = 1) -> None:
        if not self._enabled or self._finished:
            self.n += n
            return
        self.n += n
        self._try_render()

    def set(self, n: int) -> None:
        if not self._enabled or self._finished:
            self.n = n
            return
        self.n = n
        self._try_render()

    def finish(self) -> None:
        if not self._enabled or self._finished:
            return
        self.n = self.total if self.total > 0 else self.n
        self._render(time.time())
        self._finished = True

    def _try_render(self) -> None:
        now = time.time()
        if self.n < self.total and now - self._last_update < self.min_interval:
            return
        self._render(now)

    def _render(self, now: float) -> None:
        elapsed = now - self.start_time

        if self.total > 0:
            pct = self.n / self.total
            filled = int(self.width * pct)
            bar = "#" * filled + " " * (self.width - filled)

            rate = self.n / elapsed if self.n > 0 and elapsed > 0 else 0
            remaining = (self.total - self.n) / rate if rate > 0 else 0

            sys.stderr.write(
                f"\r{self.desc} [{bar}] {self.n}/{self.total}"
                f" ({pct * 100:5.1f}%)"
                f" [{_fmt_duration(elapsed)}<{_fmt_duration(remaining)}]"
            )
        else:
            rate = self.n / elapsed if elapsed > 0 else 0
            sys.stderr.write(
                f"\r{self.desc} {self.n} [{_fmt_duration(elapsed)}"
                f" ({rate:.0f} items/s)]"
            )

        if 0 < self.total <= self.n:
            sys.stderr.write("\n")
        else:
            sys.stderr.flush()

    def __enter__(self) -> "progressbar":
        return self

    def __exit__(self, *args: object) -> None:
        self.finish()

    def iter(
        self, items: Iterable[Any], total: int | None = None
    ) -> Generator[Any, None, None]:
        if total is not None:
            self.total = total
        elif hasattr(items, "__len__"):
            self.total = len(items)
        else:
            self.total = 0
        self.n = 0
        for item in items:
            yield item
            self.update()
        self.finish()
