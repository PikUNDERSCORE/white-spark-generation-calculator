# White Spark Generation Calculator

A small desktop tool for estimating white skill spark generation. Add the skills you're hoping to inherit, set how many white sparks are in the lineage, and it tells you the chance each one generates as a white spark — plus the full distribution of how many of them you'll actually land on a given run.

Built with Python's standard `tkinter`, so it has no third-party dependencies to run.

## What it does

For each skill you track, you provide:

- **Type** — white (single circle), double circle, or gold
- **Copies in lineage** — how many parents carry that spark (0–6)

It then shows the per-skill generation chance, the expected number of white sparks, and the distribution.

## Models

The base rates and lineage scaling come from a large community dataset. Three models are selectable:

| Model | Formula | Notes |
|-------|---------|-------|
| **Exponential** (recommended) | `base_rate × 1.1^copies` | Fits all three categories well (p ≥ 0.84). |
| **Piecewise-at-2** | base + a flat boost for copies 1–2, larger boost after | Best empirical fit to the data. |
| **Community linear** | `base + flat % × copies` | The original community hypothesis; kept for reference. |

Base rates: white **20%**, double circle **25%**, gold **40%**.

The exponential model is credited to [aoneko_pochi (2024)](https://x.com/aoneko_pochi/status/1762370579603304731), who first observed that a per-copy multiplicative boost fits white spark generation far better than a linear one. These are descriptive fits, not confirmed in-game formulas.
Community Linear is the baseline expectations noted in crazyfellow's parenting and gene guide
Piecewise-at-2 is based on Aya's conclusions made by their CM 10 - CM 12 room match data


## Running from source

Requires Python 3

```
python white_spark_calc.py
```

## Building a standalone .exe

With [PyInstaller](https://pyinstaller.org/):

```
pip install pyinstaller
pyinstaller --onefile --windowed white_spark_calc.py
```

## License

Personal project — use freely.
