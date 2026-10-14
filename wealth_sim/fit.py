"""Find the dial settings (chi, zeta) that best match a real wealth distribution.

For each target, the script runs the simulation over a grid of dial settings,
picks the setting whose wealth shares are closest to the target, then searches
a finer grid around it.

Examples:
    python fit.py data/wid_targets.csv
    python fit.py --top1 0.35 --top10 0.70 --bottom50 0.02

The CSV needs the columns: country, year, top_1, top_10, bottom_50
(wealth shares as fractions, e.g. 0.35 for 35%).
"""

import argparse
import csv

import numpy as np

from wealth_sim import simulate, summarize

MEASURES = ["top_1", "top_10", "bottom_50"]

# Real wealth distributions are very unequal, which in this model means low
# redistribution and modest advantage, so the grid is densest there.
COARSE_CHI = [0.02, 0.03, 0.05, 0.075, 0.1, 0.15, 0.2, 0.3, 0.5, 1.0]
COARSE_ZETA = [0.0, 0.05, 0.1, 0.15, 0.25, 0.35, 0.5, 0.75, 1.0, 1.5]


def equilibrium(chi, zeta, n_agents=2000, f=0.1, seed=0, snapshots=10):
    """Run until the distribution settles, then average a few snapshots.

    Averaging smooths out the random noise of any single moment, which matters
    for the top 1% (only 20 agents out of 2,000).
    """
    # Redistribution pulls the system to equilibrium in about 1 / (chi * f^2)
    # rounds, so run several of those, within sensible limits.
    burn_in = int(np.clip(6 / (chi * f ** 2), 3000, 60000))
    w = simulate(n_agents, burn_in, f, chi, zeta, seed)
    totals = dict.fromkeys(MEASURES + ["gini"], 0.0)
    for k in range(snapshots):
        w = simulate(n_agents, 500, f, chi, zeta, seed + k + 1, w0=w)
        for name, value in summarize(w).items():
            if name in totals:
                totals[name] += value / snapshots
    return totals


def error(sim, target):
    """Sum of squared differences in percentage points."""
    return sum((100 * (sim[m] - target[m])) ** 2 for m in MEASURES)


def search(target, chis, zetas, cache):
    best = None
    for chi in chis:
        for zeta in zetas:
            key = (round(chi, 4), round(zeta, 4))
            if key not in cache:
                cache[key] = equilibrium(*key)
            err = error(cache[key], target)
            if best is None or err < best[0]:
                best = (err, key[0], key[1])
    return best


def fit(target):
    cache = {}
    _, chi, zeta = search(target, COARSE_CHI, COARSE_ZETA, cache)
    fine_chi = [chi * s for s in (0.7, 0.85, 1.0, 1.15, 1.3)]
    step = max(0.15 * zeta, 0.02)
    fine_zeta = [max(zeta + d * step, 0.0) for d in (-2, -1, 0, 1, 2)]
    err, chi, zeta = search(target, fine_chi, fine_zeta, cache)
    return chi, zeta, err, cache[(chi, zeta)]


def report(label, target, chi, zeta, err, sim):
    print(f"\n{label}")
    print(f"  Best dials: chi = {chi:.3f}, zeta = {zeta:.2f}  (error {err:.1f})")
    print(f"  {'':12}{'Actual':>8}{'Model':>8}")
    for m in MEASURES:
        print(f"  {m:12}{target[m]:8.1%}{sim[m]:8.1%}")


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("csv", nargs="?", help="CSV of target wealth shares")
    parser.add_argument("--top1", type=float)
    parser.add_argument("--top10", type=float)
    parser.add_argument("--bottom50", type=float)
    parser.add_argument("--out", help="save fitted dials to this CSV")
    args = parser.parse_args()

    if args.csv:
        with open(args.csv) as fh:
            targets = [
                {**row, **{m: float(row[m]) for m in MEASURES}}
                for row in csv.DictReader(fh)
            ]
    elif None not in (args.top1, args.top10, args.bottom50):
        targets = [{"country": "custom", "year": "",
                    "top_1": args.top1, "top_10": args.top10,
                    "bottom_50": args.bottom50}]
    else:
        parser.error("give a CSV file or all of --top1, --top10, --bottom50")

    results = []
    for t in targets:
        chi, zeta, err, sim = fit(t)
        report(f"{t['country']} {t['year']}".strip(), t, chi, zeta, err, sim)
        results.append({"country": t["country"], "year": t["year"],
                        "chi": round(chi, 4), "zeta": round(zeta, 4),
                        "error": round(err, 2),
                        **{f"model_{m}": round(sim[m], 4) for m in MEASURES}})

    if args.out:
        with open(args.out, "w", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=list(results[0]))
            writer.writeheader()
            writer.writerows(results)
        print(f"\nSaved fitted dials to {args.out}")


if __name__ == "__main__":
    main()
