import numpy as np
import matplotlib.pyplot as plt


def cmd(args):
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
    line, = plt.plot([], [], linewidth=3.5, color="#CD5555")

    for alpha in np.arange(1, 20.01, 0.01):
        y = np.cbrt(x**2) + 0.9 * np.sqrt(np.clip(3.3 - x**2, 0, None)) * np.sin(alpha * np.pi * x)
        line.set_data(x, y)
        txt.set_text(rf"$\alpha={alpha:.2f}$")
        plt.pause(0.003)

    plt.show()
