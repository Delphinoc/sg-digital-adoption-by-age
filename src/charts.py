"""Static PNG charts for the README. The interactive dashboard is built in
Tableau Public from data/processed/ (see docs/tableau_guide.md).

Run after the pipeline:  python -m src.charts
"""
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from src.config import CHART_DIR, PROCESSED_DIR

AGE_COLORS = {"18-39": "#2a78d6", "40-59": "#eb6834", "60+": "#1baf7a"}
INK, MUTED, GRID, SURFACE = "#0b0b0b", "#52514e", "#e6e5e1", "#fcfcfb"
INDICATOR_LABELS = {
    "smartphone_ownership": "Own a smartphone",
    "internet_usage": "Use the internet",
    "online_purchase": "Bought online",
}


def _style(ax, title, subtitle):
    ax.set_facecolor(SURFACE)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.tick_params(colors=MUTED, labelsize=9, length=0)
    ax.yaxis.grid(True, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.set_title(title, loc="left", fontsize=12, color=INK, fontweight="bold", pad=22)
    ax.text(0, 1.02, subtitle, transform=ax.transAxes, fontsize=9, color=MUTED)


def chart_trend(stg: pd.DataFrame, indicator: str, fname: str) -> None:
    d = stg[(stg.indicator == indicator) & stg.segment_label.isin(AGE_COLORS)]
    fig, ax = plt.subplots(figsize=(8, 4.5), facecolor=SURFACE)
    ends = []
    for label, color in AGE_COLORS.items():
        s = d[d.segment_label == label].sort_values("year")
        ax.plot(s.year, s.pct, color=color, linewidth=2, marker="o", markersize=4, label=label)
        ends.append([s.pct.iloc[-1], label, s.pct.iloc[-1]])
    # dodge end labels so close lines don't overlap (min 6pp apart, top-down)
    ends.sort(reverse=True)
    for i in range(1, len(ends)):
        ends[i][0] = min(ends[i][0], ends[i - 1][0] - 6)
    last = d.year.max()
    for y, label, v in ends:
        ax.text(last + 0.15, y, f"{label}  {v:.0f}%", va="center", fontsize=9, color=INK)
    ax.set_ylim(0, 105)
    ax.set_xlim(d.year.min() - 0.3, last + 1.1)
    ax.set_xticks(sorted(d.year.unique()))
    ax.legend(frameon=False, fontsize=9, ncol=3, loc="lower right", labelcolor=INK)
    ax.set_ylabel("% of residents", color=MUTED, fontsize=9)
    _style(ax, f"{INDICATOR_LABELS[indicator]}, by age group",
           "Singapore residents aged 18+, IMDA Annual Survey on Infocomm Usage")
    fig.tight_layout()
    fig.savefig(CHART_DIR / fname, dpi=150)
    plt.close(fig)


def chart_ladder(ladder: pd.DataFrame, year: int) -> None:
    d = ladder[(ladder.year == year) & ladder.segment_label.isin(AGE_COLORS)]
    steps = ["smartphone_ownership", "internet_usage", "online_purchase"]
    fig, ax = plt.subplots(figsize=(8, 4.5), facecolor=SURFACE)
    width = 0.26
    for i, (label, color) in enumerate(AGE_COLORS.items()):
        vals = [d[(d.segment_label == label) & (d.indicator == s)].pct.iloc[0] for s in steps]
        xs = [x + (i - 1) * (width + 0.02) for x in range(len(steps))]
        ax.bar(xs, vals, width=width, color=color, label=label, edgecolor=SURFACE, linewidth=1)
        for x, v in zip(xs, vals):
            ax.text(x, v + 1.5, f"{v:.0f}", ha="center", fontsize=8, color=INK)
    ax.set_xticks(range(len(steps)), [INDICATOR_LABELS[s] for s in steps])
    ax.set_ylim(0, 110)
    ax.set_ylabel("% of residents", color=MUTED, fontsize=9)
    ax.legend(frameon=False, fontsize=9, ncol=3, loc="upper right", labelcolor=INK)
    _style(ax, f"The digital adoption ladder, {year}",
           "Seniors own smartphones and go online, but far fewer buy online")
    fig.tight_layout()
    fig.savefig(CHART_DIR / f"adoption_ladder_{year}.png", dpi=150)
    plt.close(fig)


def main() -> None:
    CHART_DIR.mkdir(parents=True, exist_ok=True)
    stg = pd.read_csv(PROCESSED_DIR / "stg_indicators.csv")
    ladder = pd.read_csv(PROCESSED_DIR / "mart_adoption_ladder.csv")
    chart_trend(stg, "internet_usage", "internet_usage_trend.png")
    chart_trend(stg, "online_purchase", "online_purchase_trend.png")
    chart_ladder(ladder, int(ladder.year.max()))
    print(f"Charts saved to {CHART_DIR}")


if __name__ == "__main__":
    main()
