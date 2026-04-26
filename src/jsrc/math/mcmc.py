import math
import random
from jsrc.math.core import write_output, mean


def cmd(args):
    n_iter = args.n_samples
    burnin = args.burnin
    theta = args.init
    proposal_sd = args.proposal_sd
    prior_mean = args.prior_mean
    prior_sd = args.prior_sd
    data = args.data
    chain = []
    n_accepted = 0
    for i in range(n_iter):
        theta_star = theta + random.gauss(0, proposal_sd)
        ll_current = _log_likelihood(data, theta) if data else 0
        ll_proposed = _log_likelihood(data, theta_star) if data else 0
        lp_current = _log_prior(theta, prior_mean, prior_sd)
        lp_proposed = _log_prior(theta_star, prior_mean, prior_sd)
        log_alpha = (ll_proposed + lp_proposed) - (ll_current + lp_current)
        if log_alpha >= 0 or random.random() < math.exp(log_alpha):
            theta = theta_star
            n_accepted += 1
        chain.append(theta)
    posterior = chain[burnin:]
    post_mean = mean(posterior)
    post_sd = math.sqrt(sum((x - post_mean) ** 2 for x in posterior) / (len(posterior) - 1))
    write_output([
        f"n_iter\t{n_iter}",
        f"burnin\t{burnin}",
        f"accept_rate\t{n_accepted / n_iter:.4f}",
        f"posterior_mean\t{post_mean}",
        f"posterior_sd\t{post_sd}",
        f"n_effective\t{len(posterior)}",
    ], args.output)


def _log_likelihood(data, theta):
    if not data:
        return 0.0
    n = len(data)
    return -n * 0.5 * math.log(2 * math.pi) - 0.5 * sum((x - theta) ** 2 for x in data)


def _log_prior(theta, prior_mean, prior_sd):
    return -0.5 * math.log(2 * math.pi * prior_sd ** 2) - 0.5 * ((theta - prior_mean) / prior_sd) ** 2
