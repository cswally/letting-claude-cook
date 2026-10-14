# Wealth distribution simulation

An agent-based model of how wealth spreads out (or piles up) when people trade,
with two dials for policy and advantage. Course project roadmap:

1. ~~Can AI get the basics right? Build the simulation from scratch and verify it~~
2. **Add redistribution & advantage dials** ← this folder
3. Turn the dials until the output matches real countries (WID data)
4. Compare the fitted dials with how those countries actually redistribute (OECD data)

## The model

1,000 people each start with wealth 1. Each round, everyone is paired with a random
partner and they make one trade:

- **Stake:** 10% (`f`) of the *poorer* person's wealth.
- **Winner:** a coin flip decides who gets the stake.

This is the *Yard Sale Model*. Even with a fair coin, wealth concentrates on its
own: with no dials turned, the Gini coefficient climbs toward 1.

## The dials

| Dial | Name | What it does |
| --- | --- | --- |
| `chi` (χ) | **Redistribution** | Each round everyone is taxed a share of how far they are from the average and the money is paid back equally (a flat wealth tax with an equal dividend). Higher = more equal. |
| `zeta` (ζ) | **Advantage** | Tilts the coin toward the richer person in each trade (they can afford better lawyers, information, deals). `0` = fair coin. Higher = less equal. |

Both dials are on the same time scale (from the Affine Wealth Model by Boghosian
et al.), so they can be compared directly. Roughly: when advantage beats
redistribution (`zeta > chi`), a small elite starts holding an outsized share of
the wealth.

## How to run

```bash
pip install -r requirements.txt

python run.py                           # no dials
python run.py --chi 0.5 --zeta 1.0      # set the dials
python run.py --chi 0.5 --zeta 1.0 --plot   # also save a Lorenz curve + Gini-over-time plot
python run.py --sweep                   # Gini for a grid of dial settings
```

Each run prints the measures the World Inequality Database (WID) reports, which
step 3 will compare against:

```
chi = 0.5, zeta = 1.0, 1000 agents, 20000 rounds

  Gini coefficient:   0.573
  Top 1% share:        16.5%
  Top 10% share:       49.6%
  Middle 40% share:    35.1%
  Bottom 50% share:    15.4%
```

## Dial sweep (Gini coefficient)

| | ζ = 0 | ζ = 0.25 | ζ = 0.5 | ζ = 1 | ζ = 2 |
| --- | --- | --- | --- | --- | --- |
| **χ = 0** | 0.986 | 0.999 | 0.999 | 0.999 | 0.999 |
| **χ = 0.25** | 0.480 | 0.556 | 0.644 | 0.711 | 0.766 |
| **χ = 0.5** | 0.384 | 0.417 | 0.466 | 0.573 | 0.653 |
| **χ = 1** | 0.300 | 0.317 | 0.335 | 0.389 | 0.511 |
| **χ = 2** | 0.230 | 0.237 | 0.245 | 0.263 | 0.319 |

More redistribution (down the table) → more equal. More advantage (across) → less
equal. For reference, real-world *wealth* Ginis are mostly between about 0.6 and 0.9.

## Files

- `wealth_sim.py` – the model and the inequality measures
- `run.py` – command-line tool for turning the dials
