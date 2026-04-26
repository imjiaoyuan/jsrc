import math
import random
from jsrc.math.core import mean, sd, write_output


def _median(vals):
    s = sorted(vals)
    n = len(s)
    if n % 2 == 1:
        return s[n // 2]
    return (s[n // 2 - 1] + s[n // 2]) / 2



def cmd(args):
    n = args.n_samples
    mu = args.mean
    sigma = args.sd
    samples = [_normal_sample(mu, sigma) for _ in range(n)]
    stat = args.stat
    if stat == "mean":
        value = mean(samples)
    elif stat == "median":
        value = _median(samples)
    elif stat == "sd":
        value = sd(samples)
    elif stat == "min":
        value = min(samples)
    elif stat == "max":
        value = max(samples)
    write_output([
        f"n\t{n}",
        f"mean\t{mu}",
        f"sd\t{sigma}",
        f"statistic\t{stat}",
        f"value\t{value}",
    ], args.output)


def _normal_sample(mu, sigma):
    u1 = random.random()
    u2 = random.random()
    z = math.sqrt(-2.0 * math.log(u1)) * math.cos(2.0 * math.pi * u2)
    return mu + sigma * z
