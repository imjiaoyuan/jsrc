import math
from jsrc.math.core import write_output


def cmd(args):
    states = args.states
    observations = args.observations
    n_states = len(states)
    if len(args.trans_probs) != n_states * n_states:
        print(f"Error: transition matrix needs {n_states * n_states} values")
        return
    if len(args.emit_probs) != n_states * len(set(observations)):
        print("Error: emission matrix dimensions mismatch")
        return
    if len(args.start_probs) != n_states:
        print(f"Error: start probabilities need {n_states} values")
        return
    obs_set = sorted(set(observations))
    n_obs = len(obs_set)
    obs_map = {o: i for i, o in enumerate(obs_set)}
    trans = [[args.trans_probs[i * n_states + j] for j in range(n_states)] for i in range(n_states)]
    emit = [[args.emit_probs[i * n_obs + j] for j in range(n_obs)] for i in range(n_states)]
    start = args.start_probs
    obs_seq = [obs_map[o] for o in observations]
    T = len(obs_seq)
    if args.task == "forward":
        alpha = _forward(obs_seq, n_states, start, trans, emit)
        log_prob = math.log(sum(alpha[-1])) if sum(alpha[-1]) > 0 else -float("inf")
        output_lines = [f"task\tforward", f"log_probability\t{log_prob:.6g}"]
        for t, probs in enumerate(alpha):
            for s, p in zip(states, probs):
                output_lines.append(f"t{t}\t{s}\t{p:.6g}")
        write_output(output_lines, args.output)
    elif args.task == "backward":
        beta = _backward(obs_seq, n_states, trans, emit)
        output_lines = [f"task\tbackward"]
        for t, probs in enumerate(beta):
            for s, p in zip(states, probs):
                output_lines.append(f"t{t}\t{s}\t{p:.6g}")
        write_output(output_lines, args.output)
    else:
        path, prob = _viterbi(obs_seq, n_states, start, trans, emit)
        output_lines = [
            f"task\tviterbi",
            f"log_probability\t{prob:.6g}",
            f"path\t{' '.join(states[s] for s in path)}",
        ]
        for t, s in enumerate(path):
            output_lines.append(f"t{t}\t{states[s]}")
        write_output(output_lines, args.output)


def _forward(obs_seq, n_states, start, trans, emit):
    T = len(obs_seq)
    alpha = [[0.0] * n_states for _ in range(T)]
    for s in range(n_states):
        alpha[0][s] = start[s] * emit[s][obs_seq[0]]
    for t in range(1, T):
        for s in range(n_states):
            alpha[t][s] = sum(alpha[t - 1][s2] * trans[s2][s] for s2 in range(n_states)) * emit[s][obs_seq[t]]
    return alpha


def _backward(obs_seq, n_states, trans, emit):
    T = len(obs_seq)
    beta = [[0.0] * n_states for _ in range(T)]
    for s in range(n_states):
        beta[T - 1][s] = 1.0
    for t in range(T - 2, -1, -1):
        for s in range(n_states):
            beta[t][s] = sum(trans[s][s2] * emit[s2][obs_seq[t + 1]] * beta[t + 1][s2] for s2 in range(n_states))
    return beta


def _viterbi(obs_seq, n_states, start, trans, emit):
    T = len(obs_seq)
    V = [[0.0] * n_states for _ in range(T)]
    back = [[0] * n_states for _ in range(T)]
    for s in range(n_states):
        V[0][s] = math.log(start[s] + 1e-30) + math.log(emit[s][obs_seq[0]] + 1e-30)
    for t in range(1, T):
        for s in range(n_states):
            vals = [V[t - 1][s2] + math.log(trans[s2][s] + 1e-30) for s2 in range(n_states)]
            best_s = max(range(n_states), key=lambda i: vals[i])
            V[t][s] = vals[best_s] + math.log(emit[s][obs_seq[t]] + 1e-30)
            back[t][s] = best_s
    best_last = max(range(n_states), key=lambda s: V[T - 1][s])
    prob = V[T - 1][best_last]
    path = [best_last]
    for t in range(T - 1, 0, -1):
        path.insert(0, back[t][path[0]])
    return path, prob
