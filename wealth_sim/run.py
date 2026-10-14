"""Turn the dials and see the resulting wealth distribution.

Examples:
    python run.py                          # no dials: wealth concentrates
    python run.py --chi 0.5 --zeta 0.2     # set both dials
    python run.py --chi 0.5 --zeta 0.2 --plot
    python run.py --sweep                  # Gini for a grid of dial settings
"""

import argparse

from wealth_sim import simulate, summarize


def print_summary(stats):
    print(f"  Gini coefficient:   {stats['gini']:.3f}")
    print(f"  Top 1% share:       {stats['top_1']:6.1%}")
    print(f"  Top 10% share:      {stats['top_10']:6.1%}")
    print(f"  Middle 40% share:   {stats['middle_40']:6.1%}")
    print(f"  Bottom 50% share:   {stats['bottom_50']:6.1%}")


def plot(w, history, args):
    import matplotlib.pyplot as plt
    import numpy as np

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.5))

    sorted_w = np.sort(w)
    people = np.linspace(0, 1, len(w) + 1)
    lorenz = np.concatenate([[0], np.cumsum(sorted_w) / sorted_w.sum()])
    ax1.plot(people, lorenz, label="Simulation")
    ax1.plot([0, 1], [0, 1], "--", color="gray", label="Perfect equality")
    ax1.set_xlabel("Share of people (poorest to richest)")
    ax1.set_ylabel("Share of total wealth")
    ax1.set_title("Lorenz curve")
    ax1.legend()

    rounds, ginis = zip(*history)
    ax2.plot(rounds, ginis)
    ax2.set_xlabel("Round")
    ax2.set_ylabel("Gini coefficient")
    ax2.set_ylim(0, 1)
    ax2.set_title("Inequality over time")

    fig.suptitle(f"chi = {args.chi}, zeta = {args.zeta}")
    fig.tight_layout()
    out = f"wealth_chi{args.chi}_zeta{args.zeta}.png"
    fig.savefig(out, dpi=120)
    print(f"\nSaved plot to {out}")


def sweep(args):
    chis = [0.0, 0.25, 0.5, 1.0, 2.0]
    zetas = [0.0, 0.25, 0.5, 1.0, 2.0]
    print("Gini coefficient for each dial setting\n")
    print("          " + "".join(f"zeta={z:<6}" for z in zetas))
    for chi in chis:
        row = []
        for zeta in zetas:
            w = simulate(args.agents, args.rounds, args.f, chi, zeta, args.seed)
            row.append(summarize(w)["gini"])
        print(f"chi={chi:<5}" + "".join(f"{g:<11.3f}" for g in row))


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--chi", type=float, default=0.0, help="redistribution dial")
    parser.add_argument("--zeta", type=float, default=0.0, help="advantage dial")
    parser.add_argument("--f", type=float, default=0.1, help="fraction staked per trade")
    parser.add_argument("--agents", type=int, default=1000)
    parser.add_argument("--rounds", type=int, default=20000)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--plot", action="store_true", help="save a Lorenz curve plot")
    parser.add_argument("--sweep", action="store_true", help="grid of dial settings")
    args = parser.parse_args()

    if args.sweep:
        sweep(args)
        return

    record = max(args.rounds // 200, 1) if args.plot else 0
    result = simulate(args.agents, args.rounds, args.f, args.chi, args.zeta,
                      args.seed, record_every=record)
    w, history = result if record else (result, None)

    print(f"chi = {args.chi}, zeta = {args.zeta}, "
          f"{args.agents} agents, {args.rounds} rounds\n")
    print_summary(summarize(w))
    if args.plot:
        plot(w, history, args)


if __name__ == "__main__":
    main()
