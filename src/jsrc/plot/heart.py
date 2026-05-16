import os
import sys
from argparse import Namespace
from typing import Any

import numpy as np


def _load_backend(matplotlib: Any, backend: str) -> Any | None:
    try:
        matplotlib.use(backend, force=True)
        import matplotlib.pyplot as plt
    except (ImportError, ValueError):
        return None
    if "agg" in matplotlib.get_backend().lower():
        return None
    return plt


def _load_interactive_pyplot() -> Any:
    try:
        import matplotlib
    except ImportError as exc:
        raise SystemExit(
            "matplotlib is required for this command. Install it with: pip install matplotlib"
        ) from exc

    env_backend = os.getenv("MPLBACKEND", "").strip()
    if env_backend:
        import matplotlib.pyplot as plt

        if "agg" in matplotlib.get_backend().lower():
            raise SystemExit(
                "jsrc plot heart requires an interactive matplotlib backend. "
                "Current MPLBACKEND is non-interactive."
            )
        return plt

    if sys.platform.startswith("linux") and not (
        os.getenv("DISPLAY") or os.getenv("WAYLAND_DISPLAY")
    ):
        raise SystemExit(
            "No graphical display detected. Set DISPLAY/WAYLAND_DISPLAY or run in a desktop session."
        )

    for backend in ("TkAgg", "QtAgg", "Qt5Agg", "GTK3Agg", "WXAgg", "MacOSX"):
        plt = _load_backend(matplotlib, backend)
        if plt is not None:
            return plt

    raise SystemExit(
        "No interactive matplotlib backend is available. "
        "Install a GUI backend (for example python3-tk or PyQt6)."
    )


def cmd(args: Namespace) -> None:
    plt = _load_interactive_pyplot()
    x = np.arange(-1.8, 1.8, 0.005)

    plt.figure(figsize=(12, 10))
    plt.grid(True)
    plt.axis([-3, 3, -2, 4])

    plt.text(
        0,
        3.3,
        r"$f(x)=x^{\frac{2}{3}}+0.9(3.3-x^2)^{\frac{1}{2}}\sin(\alpha\pi x)$",
        fontsize=28,
        ha="center",
    )
    txt = plt.text(-0.35, 2.9, "", fontsize=26, ha="left")
    (line,) = plt.plot([], [], linewidth=3.5, color="#CD5555")

    for alpha in np.arange(1, 20.01, 0.01):
        y = np.cbrt(x**2) + 0.9 * np.sqrt(np.clip(3.3 - x**2, 0, None)) * np.sin(
            alpha * np.pi * x
        )
        line.set_data(x, y)
        txt.set_text(rf"$\alpha={alpha:.2f}$")
        plt.pause(0.003)

    plt.show()


def register(subparsers: Any) -> None:
    p = subparsers.add_parser("heart", help="Plot heart curve")
    p.set_defaults(func=cmd)
