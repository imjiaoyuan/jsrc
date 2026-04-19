from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


class EllipticFourier:
    @staticmethod
    def calculate(contour: np.ndarray, order: int = 20, normalize: bool = True) -> np.ndarray:
        contour = contour.squeeze()
        if contour.ndim != 2 or contour.shape[0] < 3:
            return np.zeros((order, 4), dtype=float)

        dx = np.diff(contour[:, 0])
        dy = np.diff(contour[:, 1])
        dt = np.sqrt(dx**2 + dy**2)
        t = np.concatenate(([0.0], np.cumsum(dt)))
        total_len = float(t[-1])
        if total_len < 1e-8:
            return np.zeros((order, 4), dtype=float)

        valid = dt > 1e-12
        if not np.any(valid):
            return np.zeros((order, 4), dtype=float)

        phi = (2.0 * np.pi * t) / total_len
        coeffs = np.zeros((order, 4), dtype=float)
        dphi_cos = {}
        dphi_sin = {}

        for n in range(1, order + 1):
            phi_n = phi * n
            dphi_cos[n] = np.cos(phi_n[1:]) - np.cos(phi_n[:-1])
            dphi_sin[n] = np.sin(phi_n[1:]) - np.sin(phi_n[:-1])

        dx_over_dt = np.zeros_like(dx, dtype=float)
        dy_over_dt = np.zeros_like(dy, dtype=float)
        dx_over_dt[valid] = dx[valid] / dt[valid]
        dy_over_dt[valid] = dy[valid] / dt[valid]

        for n in range(1, order + 1):
            const = total_len / (2.0 * (n * np.pi) ** 2)
            an = const * np.sum(dx_over_dt * dphi_cos[n])
            bn = const * np.sum(dx_over_dt * dphi_sin[n])
            cn = const * np.sum(dy_over_dt * dphi_cos[n])
            dn = const * np.sum(dy_over_dt * dphi_sin[n])
            coeffs[n - 1] = [an, bn, cn, dn]

        if normalize:
            coeffs = EllipticFourier.normalize(coeffs)
        return coeffs

    @staticmethod
    def normalize(coeffs: np.ndarray) -> np.ndarray:
        if len(coeffs) == 0:
            return coeffs

        a1, b1, c1, d1 = coeffs[0]
        theta = 0.5 * np.arctan2(
            2.0 * (a1 * b1 + c1 * d1),
            (a1**2 + c1**2 - b1**2 - d1**2),
        )

        cos_t, sin_t = np.cos(theta), np.sin(theta)
        a1_s = a1 * cos_t + c1 * sin_t
        c1_s = -a1 * sin_t + c1 * cos_t

        psi = np.arctan2(c1_s, a1_s)
        rot_matrix = np.array([[cos_t, sin_t], [-sin_t, cos_t]])
        scale = float(np.sqrt(a1_s**2 + c1_s**2))
        if scale < 1e-8:
            scale = 1.0

        out = []
        for idx, (an, bn, cn, dn) in enumerate(coeffs, start=1):
            mat_phi = np.array(
                [
                    [np.cos(idx * psi), -np.sin(idx * psi)],
                    [np.sin(idx * psi), np.cos(idx * psi)],
                ]
            )
            vec_ab = mat_phi @ np.array([an, bn])
            vec_cd = mat_phi @ np.array([cn, dn])
            vec_ac = rot_matrix @ np.array([vec_ab[0], vec_cd[0]])
            vec_bd = rot_matrix @ np.array([vec_ab[1], vec_cd[1]])
            out.append([vec_ac[0] / scale, vec_bd[0] / scale, vec_ac[1] / scale, vec_bd[1] / scale])
        return np.array(out)

    @staticmethod
    def reconstruct(coeffs: np.ndarray, num_points: int = 300) -> np.ndarray:
        t = np.linspace(0.0, 1.0, num_points)
        xt = np.zeros(num_points)
        yt = np.zeros(num_points)
        for n, (an, bn, cn, dn) in enumerate(coeffs, start=1):
            xt += an * np.cos(2.0 * np.pi * n * t) + bn * np.sin(2.0 * np.pi * n * t)
            yt += cn * np.cos(2.0 * np.pi * n * t) + dn * np.sin(2.0 * np.pi * n * t)
        return np.stack([xt, yt], axis=1)


def _iter_contours(input_path: str) -> list[Path]:
    path = Path(input_path)
    if path.is_file():
        if path.suffix.lower() != ".npy":
            raise ValueError(f"Input file must be .npy: {input_path}")
        return [path]
    if not path.is_dir():
        raise FileNotFoundError(f"Input path not found: {input_path}")
    return sorted(path.glob("*.npy"))


def _center_contour(contour: np.ndarray) -> np.ndarray:
    contour = contour.squeeze()
    if contour.ndim != 2 or contour.shape[1] != 2:
        raise ValueError(f"Invalid contour shape: {contour.shape}")

    centroid_x = float(np.mean(contour[:, 0]))
    centroid_y = float(np.mean(contour[:, 1]))
    centered_x = contour[:, 0] - centroid_x
    centered_y = -(contour[:, 1] - centroid_y)
    return np.stack([centered_x, centered_y], axis=1)


def _plot_comparison(contour: np.ndarray, reconstruction: np.ndarray, output_png: Path, harmonics: int):
    plt.figure(figsize=(6, 6))
    plt.plot(contour[:, 0], contour[:, 1], "k-", alpha=0.35, linewidth=2.5, label="Original")
    plt.plot(reconstruction[:, 0], reconstruction[:, 1], "r--", linewidth=1.5, label=f"EFD (Order {harmonics})")
    plt.axhline(0, color="gray", alpha=0.3)
    plt.axvline(0, color="gray", alpha=0.3)
    plt.legend()
    plt.axis("equal")
    plt.tight_layout()
    plt.savefig(output_png, dpi=300)
    plt.close()


def cmd(args):
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    contour_files = _iter_contours(args.input)
    if not contour_files:
        print(f"No .npy files found in {args.input}")
        return

    for npy_file in contour_files:
        file_name = npy_file.stem
        contour = np.load(npy_file)
        centered = _center_contour(contour)

        coeffs_norm = EllipticFourier.calculate(centered, order=args.harmonics, normalize=True)
        np.savetxt(
            output_dir / f"{file_name}_efd.csv",
            coeffs_norm,
            delimiter=",",
            header="an,bn,cn,dn",
            comments="",
        )

        if not args.no_plot:
            coeffs_raw = EllipticFourier.calculate(centered, order=args.harmonics, normalize=False)
            reconstruction = EllipticFourier.reconstruct(coeffs_raw, num_points=args.points)
            _plot_comparison(centered, reconstruction, output_dir / f"{file_name}_analysis.png", args.harmonics)

        print(f"Processed: {file_name}")
