import numpy as np


def cmd(args):
    try:
        import plotly.graph_objects as go
    except ImportError as exc:
        raise SystemExit("plotly is required for this command. Install it with: pip install plotly") from exc

    x_vec = np.linspace(0, 1, 25)
    t_vec = np.linspace(0, 575, 1151) / 575 * 20 * np.pi + 4 * np.pi
    x, t = np.meshgrid(x_vec, t_vec)

    p = (np.pi / 2) * np.exp(-t / (8 * np.pi))
    change = np.sin(15 * t) / 150
    u = 1 - (1 - np.mod(3.6 * t, 2 * np.pi) / np.pi) ** 4 / 2 + change

    y = 2 * (x**2 - x) ** 2 * np.sin(p)
    r = u * (x * np.sin(p) + y * np.cos(p))

    xx = r * np.cos(t)
    yy = r * np.sin(t)
    zz = u * (x * np.cos(p) - y * np.sin(p))

    fig = go.Figure()
    fig.add_trace(
        go.Surface(
            x=xx,
            y=yy,
            z=zz,
            colorscale="Reds",
            opacity=0.5,
            showscale=False,
        )
    )
    fig.add_trace(
        go.Scatter3d(
            x=[0, 0, 0, 0],
            y=[0, 0, 0, 0],
            z=np.linspace(-0.5, 0, 4),
            mode="lines",
            line={"color": "green", "width": 8},
            showlegend=False,
        )
    )
    fig.update_layout(
        scene={
            "xaxis": {"visible": False},
            "yaxis": {"visible": False},
            "zaxis": {"visible": False},
            "aspectmode": "data",
        },
        margin={"l": 0, "r": 0, "b": 0, "t": 0},
    )
    fig.show()
