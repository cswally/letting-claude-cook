# Data

## `wid_targets.csv` (step 3, not yet downloaded)

Wealth shares from the World Inequality Database (https://wid.world), one row
per country and year:

| column | WID variable | meaning |
| --- | --- | --- |
| `top_1` | `shweal_p99p100_992_j` | share of net personal wealth held by the top 1% |
| `top_10` | `shweal_p90p100_992_j` | share held by the top 10% |
| `bottom_50` | `shweal_p0p50_992_j` | share held by the bottom 50% |

All values are fractions (0.35 = 35%), for adults (`992`) with wealth split
equally between spouses (`j`).

Example layout:

```
country,year,top_1,top_10,bottom_50
US,2022,...,...,...
```
