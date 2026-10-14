"""Yard Sale wealth-exchange simulation with redistribution and advantage dials.

Base model (Yard Sale Model):
    Agents are paired at random. In each pair the stake is a fraction `f` of the
    poorer agent's wealth, and a coin flip decides who wins it. Total wealth is
    conserved. With a fair coin and nothing else, wealth slowly concentrates
    into fewer and fewer hands.

Dial 1 - redistribution (chi):
    Every round, each agent is taxed a share of their distance from the average
    wealth, and the proceeds are paid back equally. Equivalent to a flat wealth
    tax with an equal dividend: w <- w + chi * dt * (mean - w).

Dial 2 - advantage (zeta), "wealth-attained advantage":
    The coin is tilted toward the richer agent of the pair:
        P(i wins) = 1/2 * (1 + zeta * f * (w_i - w_j) / mean)
    zeta = 0 is a fair coin; larger zeta means the rich win more often.

Time scaling follows the Affine Wealth Model (Boghosian et al.): each round
advances time by dt = f**2, so chi and zeta are measured on the same scale and
can be compared directly to each other.
"""

import numpy as np


def simulate(n_agents=1000, rounds=20000, f=0.1, chi=0.0, zeta=0.0,
             seed=None, record_every=0):
    """Run the simulation and return final wealth (and optional history).

    Every agent starts with wealth 1, so the average wealth is always 1.

    Args:
        n_agents: number of agents (must be even).
        rounds: number of rounds; each round every agent trades once.
        f: fraction of the poorer agent's wealth staked per trade.
        chi: redistribution dial (>= 0).
        zeta: advantage dial (>= 0).
        seed: random seed for reproducibility.
        record_every: if > 0, also return a list of (round, gini) snapshots.
    """
    if n_agents % 2:
        raise ValueError("n_agents must be even")
    rng = np.random.default_rng(seed)
    w = np.ones(n_agents)
    mean = 1.0
    dt = f ** 2
    history = []

    for r in range(rounds):
        order = rng.permutation(n_agents)
        i, j = order[: n_agents // 2], order[n_agents // 2:]
        wi, wj = w[i], w[j]

        stake = f * np.minimum(wi, wj)
        p_i_wins = 0.5 * (1 + zeta * f * (wi - wj) / mean)
        p_i_wins = np.clip(p_i_wins, 0.0, 1.0)
        sign = np.where(rng.random(n_agents // 2) < p_i_wins, 1.0, -1.0)

        w[i] += sign * stake
        w[j] -= sign * stake

        if chi:
            w += chi * dt * (mean - w)

        if record_every and r % record_every == 0:
            history.append((r, gini(w)))

    return (w, history) if record_every else w


def gini(w):
    """Gini coefficient: 0 = perfect equality, 1 = one agent has everything."""
    w = np.sort(w)
    n = len(w)
    ranks = np.arange(1, n + 1)
    return float((2 * ranks - n - 1) @ w / (n * w.sum()))


def share(w, top=None, bottom=None):
    """Share of total wealth held by the top or bottom fraction of agents."""
    w = np.sort(w)
    n = len(w)
    if top is not None:
        return float(w[n - int(round(top * n)):].sum() / w.sum())
    return float(w[: int(round(bottom * n))].sum() / w.sum())


def summarize(w):
    """The distribution measures reported by the World Inequality Database."""
    return {
        "gini": gini(w),
        "top_1": share(w, top=0.01),
        "top_10": share(w, top=0.10),
        "middle_40": 1 - share(w, top=0.10) - share(w, bottom=0.50),
        "bottom_50": share(w, bottom=0.50),
    }
