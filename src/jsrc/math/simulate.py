import math
from jsrc.math.core import write_output


def cmd(args):
    model = args.model
    dt = args.dt
    tmax = args.tmax
    params = args.params
    init = args.init
    n_steps = int(tmax / dt)
    if model == "sir":
        result = _sir(dt, n_steps, params, init)
    elif model == "lotkavolterra":
        result = _lotkavolterra(dt, n_steps, params, init)
    elif model == "pk1":
        result = _pk1(dt, n_steps, params, init)
    elif model == "emax":
        result = _emax(dt, n_steps, params, init)
    elif model == "gompertz":
        result = _gompertz(dt, n_steps, params, init)
    elif model == "logistic":
        result = _logistic(dt, n_steps, params, init)
    else:
        print(f"Error: unknown model '{model}'")
        return
    lines = [result[0]]
    for row in result[1:]:
        lines.append("\t".join(f"{v:.6g}" for v in row))
    write_output(lines, args.output)


def _sir(dt, n_steps, params, init):
    beta, gamma = params[0], params[1] if len(params) > 1 else 0.1
    S = init[0] if init and len(init) > 0 else 990.0
    I = init[1] if init and len(init) > 1 else 10.0
    R = init[2] if init and len(init) > 2 else 0.0
    header = "t\tS\tI\tR"
    rows = []
    t = 0.0
    for _ in range(n_steps):
        rows.append((t, S, I, R))
        dS = -beta * S * I / (S + I + R) * dt
        dI = (beta * S * I / (S + I + R) - gamma * I) * dt
        dR = gamma * I * dt
        S += dS
        I += dI
        R += dR
        t += dt
        if I < 0.01 and t > 1:
            break
    return [header] + rows


def _lotkavolterra(dt, n_steps, params, init):
    alpha, beta, gamma, delta = params[0], params[1], params[2], params[3] if len(params) > 3 else 1.0
    prey = init[0] if init and len(init) > 0 else 40.0
    pred = init[1] if init and len(init) > 1 else 9.0
    header = "t\tprey\tpredator"
    rows = []
    t = 0.0
    for _ in range(n_steps):
        rows.append((t, prey, pred))
        d_prey = (alpha * prey - beta * prey * pred) * dt
        d_pred = (delta * prey * pred - gamma * pred) * dt
        prey += d_prey
        pred += d_pred
        t += dt
        if prey < 0:
            prey = 0
        if pred < 0:
            pred = 0
    return [header] + rows


def _pk1(dt, n_steps, params, init):
    ka, ke, F_dose_V = params[0], params[1], params[2] if len(params) > 2 else 10.0
    C = init[0] if init and len(init) > 0 else 0.0
    A = init[1] if init and len(init) > 1 else F_dose_V
    header = "t\tC\tA"
    rows = []
    t = 0.0
    for _ in range(n_steps):
        rows.append((t, C, A))
        dA = -ka * A * dt
        dC = (ka * A - ke * C) * dt
        A += dA
        C += dC
        t += dt
        if C < 0.001 and A < 0.001 and t > 1:
            break
    return [header] + rows


def _emax(dt, n_steps, params, init):
    E0, Emax, EC50, ke = params[0], params[1], params[2], params[3] if len(params) > 3 else 0.1
    dose = params[4] if len(params) > 4 else 10.0
    C = init[0] if init and len(init) > 0 else dose
    header = "t\tC\tE"
    rows = []
    t = 0.0
    for _ in range(n_steps):
        E = E0 + Emax * C / (EC50 + C)
        rows.append((t, C, E))
        dC = -ke * C * dt
        C += dC
        t += dt
        if C < 0.001:
            break
    return [header] + rows


def _gompertz(dt, n_steps, params, init):
    r, K = params[0], params[1] if len(params) > 1 else 100.0
    N = init[0] if init and len(init) > 0 else 1.0
    header = "t\tN"
    rows = []
    t = 0.0
    for _ in range(n_steps):
        rows.append((t, N))
        dN = r * N * math.log(K / max(N, 1e-10)) * dt if N > 0 else 0
        N += dN
        t += dt
        if N >= K * 0.999:
            break
    return [header] + rows


def _logistic(dt, n_steps, params, init):
    r, K = params[0], params[1] if len(params) > 1 else 100.0
    N = init[0] if init and len(init) > 0 else 1.0
    header = "t\tN"
    rows = []
    t = 0.0
    for _ in range(n_steps):
        rows.append((t, N))
        dN = r * N * (1 - N / K) * dt
        N += dN
        t += dt
        if N >= K * 0.999:
            break
    return [header] + rows
