from __future__ import annotations

import gzip
import sys
import time
from collections.abc import Generator, Iterable, Sized
from pathlib import Path
from typing import IO, TypeVar

T = TypeVar("T")


class JsrcError(Exception):
    """Base exception for all jsrc errors."""

    pass


class ValidationError(JsrcError):
    """Raised when input validation fails."""

    pass


class DataFormatError(JsrcError):
    """Raised when data format is invalid or cannot be parsed."""

    pass


class ResourceNotFoundError(JsrcError):
    """Raised when a required resource (file, ID, etc.) is not found."""

    pass


class DependencyError(JsrcError):
    """Raised when an external dependency is missing or fails."""

    pass


class ConfigurationError(JsrcError):
    """Raised when configuration is invalid or incomplete."""

    pass


def parse_gff_attributes(attr_string: str) -> dict[str, str]:
    """Parse GFF/GTF attribute string into a dictionary."""
    attrs: dict[str, str] = {}
    for item in attr_string.strip().strip(";").split(";"):
        if "=" in item:
            key, value = item.strip().split("=", 1)
            attrs[key] = value.strip('"')
        elif " " in item:
            parts = item.strip().split(None, 1)
            if len(parts) == 2:
                attrs[parts[0]] = parts[1].strip('"')
    return attrs


def setup_matplotlib():
    """Configure matplotlib to use Agg backend for headless operation."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    return plt


def open_text(path: str | Path) -> IO[str]:
    path_str = str(path)
    if path_str.endswith(".gz"):
        return gzip.open(path_str, "rt", encoding="utf-8")
    return open(path_str, encoding="utf-8")


def nxx(lengths: list[int], pct: float) -> int:
    if not lengths:
        return 0
    target = sum(lengths) * pct
    acc = 0
    for v in sorted(lengths, reverse=True):
        acc += v
        if acc >= target:
            return v
    return 0


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

    def __enter__(self) -> progressbar:
        return self

    def __exit__(self, *args: object) -> None:
        self.finish()

    def iter(
        self, items: Iterable[T], total: int | None = None
    ) -> Generator[T, None, None]:
        if total is not None:
            self.total = total
        elif isinstance(items, Sized):
            self.total = len(items)
        else:
            self.total = 0
        self.n = 0
        for item in items:
            yield item
            self.update()
        self.finish()
