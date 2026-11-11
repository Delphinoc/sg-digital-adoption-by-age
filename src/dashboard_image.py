"""Static one-page dashboard image for the README (outputs/dashboard.png).

Run after the pipeline:  python -m src.dashboard_image
"""
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from src.charts import AGE_COLORS, GRID, INK, MUTED, SURFACE
from src.config import CHART_DIR, PROCESSED_DIR

IND_COLORS = {"smartphone_ownership": "#eda100", "internet_usage": "#e87ba4", "online_purchase": "#6250d6"}
IND_LABELS = {"smartphone_ownership": "Own a smartphone", "internet_usage": "Use the internet",
              "online_purchase": "Bought online"}


def _axes_style(ax, title):
    ax.set_facecolor(SURFACE)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.tick_params(colors=MUTED, labelsize=8, length=0)
    ax.yaxis.grid(True, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.set_title(title, loc="left", fontsize=10.5, color=INK, fontweight="bold", pad=8)


def _end_labels(ax, ends, fmt, x):
    ends.sort(key=lambda e: -e[0])
    ys = []
    for v, _, _ in ends:
        y = v if not ys else min(v, ys[-1] - 7)
        ys.append(y)
    for (v, label, color), y in zip(ends, ys):
        ax.text(x + 0.2, y, f"{label} {fmt(v)}", va="center", fontsize=8, color=INK)


def main() -> None:
    stg = pd.read_csv(PROCESSED_DIR / "stg_indicators.csv")
    gap = pd.read_csv(PROCESSED_DIR / "mart_age_gap.csv")
    change = pd.read_csv(PROCESSED_DIR / "mart_gap_change.csv").set_index("indicator")
    latest, first = int(stg.year.max()), int(stg.year.min())

    def val(ind, seg, yr):
        return stg[(stg.indicator == ind) & (stg.segment == seg) & (stg.year == yr)].pct.iloc[0]

    fig = plt.figure(figsize=(12, 9.6), facecolor=SURFACE)
    gs = fig.add_gridspec(3, 4, height_ratios=[0.55, 1.25, 1.25], hspace=0.55, wspace=0.35,
                          left=0.05, right=0.97, top=0.88, bottom=0.05)
    fig.text(0.05, 0.955, f"Singapore's senior digital divide, {first}–{latest}", fontsize=17,
             color=INK, fontweight="bold")
    fig.text(0.05, 0.925, "IMDA Annual Survey on Infocomm Usage (via data.gov.sg), Singapore residents aged 18+",
             fontsize=9.5, color=MUTED)

    tiles = [
        ("Seniors (60+) using the internet", f"{val('internet_usage', 'age_60_plus', latest):.1f}%",
         f"+{val('internet_usage', 'age_60_plus', latest) - val('internet_usage', 'age_60_plus', first):.1f} pts since {first}"),
        ("Seniors (60+) who bought online", f"{val('online_purchase', 'age_60_plus', latest):.1f}%",
         f"vs {val('online_purchase', 'age_18_39', latest):.1f}% of 18–39 year-olds"),
        ("Internet-use gap, 18–39 vs 60+", f"{change.loc['internet_usage', 'gap_pp_latest']:.1f} pts",
         f"down from {change.loc['internet_usage', 'gap_pp_first']:.1f} pts in {first}"),
        ("Seniors-only homes with internet",
         f"{val('household_internet_access', 'hh_seniors_only', latest):.1f}%",
         f"+{val('household_internet_access', 'hh_seniors_only', latest) - val('household_internet_access', 'hh_seniors_only', first):.1f} pts since {first}"),
    ]
    for i, (label, big, sub) in enumerate(tiles):
        ax = fig.add_subplot(gs[0, i])
        ax.set_xticks([]); ax.set_yticks([])
        ax.set_facecolor("#f3f2ef")
        for s in ax.spines.values():
            s.set_color(GRID)
        ax.text(0.06, 0.78, label, fontsize=8.5, color=MUTED, transform=ax.transAxes)
        ax.text(0.06, 0.38, big, fontsize=22, color=INK, transform=ax.transAxes)
        ax.text(0.06, 0.1, sub, fontsize=8, color=MUTED, transform=ax.transAxes)

    # ladder
    ax = fig.add_subplot(gs[1, :2])
    steps = list(IND_LABELS)
    w = 0.26
    for i, (label, color) in enumerate(AGE_COLORS.items()):
        seg = {"18-39": "age_18_39", "40-59": "age_40_59", "60+": "age_60_plus"}[label]
        vals = [val(s, seg, latest) for s in steps]
        xs = [x + (i - 1) * (w + 0.02) for x in range(3)]
        ax.bar(xs, vals, width=w, color=color, label=label, edgecolor=SURFACE)
        for x, v in zip(xs, vals):
            ax.text(x, v + 1.5, f"{v:.0f}", ha="center", fontsize=7.5, color=INK)
    ax.set_xticks(range(3), [IND_LABELS[s] for s in steps])
    ax.set_ylim(0, 112)
    ax.legend(frameon=False, fontsize=8, ncol=3, loc="upper right", labelcolor=INK)
    _axes_style(ax, f"Where each age group drops off the adoption ladder, {latest} (%)")

    # trend: internet use
    ax = fig.add_subplot(gs[1, 2:])
    ends = []
    for label, color in AGE_COLORS.items():
        seg = {"18-39": "age_18_39", "40-59": "age_40_59", "60+": "age_60_plus"}[label]
        s = stg[(stg.indicator == "internet_usage") & (stg.segment == seg)].sort_values("year")
        ax.plot(s.year, s.pct, color=color, linewidth=2, marker="o", markersize=3.5, label=label)
        ends.append((s.pct.iloc[-1], label, color))
    _end_labels(ax, ends, lambda v: f"{v:.0f}%", latest)
    ax.set_ylim(0, 105); ax.set_xlim(first - 0.3, latest + 1.4)
    ax.set_xticks(range(first, latest + 1))
    _axes_style(ax, "Internet use by age group (%)")

    # trend: online purchase
    ax = fig.add_subplot(gs[2, :2])
    ends = []
    for label, color in AGE_COLORS.items():
        seg = {"18-39": "age_18_39", "40-59": "age_40_59", "60+": "age_60_plus"}[label]
        s = stg[(stg.indicator == "online_purchase") & (stg.segment == seg)].sort_values("year")
        ax.plot(s.year, s.pct, color=color, linewidth=2, marker="o", markersize=3.5)
        ends.append((s.pct.iloc[-1], label, color))
    _end_labels(ax, ends, lambda v: f"{v:.0f}%", latest)
    ax.set_ylim(0, 105); ax.set_xlim(first - 0.3, latest + 1.4)
    ax.set_xticks(range(first, latest + 1))
    _axes_style(ax, "Bought online, by age group (%)")

    # gap over time
    ax = fig.add_subplot(gs[2, 2:])
    ends = []
    for ind, color in IND_COLORS.items():
        s = gap[gap.indicator == ind].sort_values("year")
        ax.plot(s.year, s.gap_pp, color=color, linewidth=2, marker="o", markersize=3.5, label=IND_LABELS[ind])
        ends.append((s.gap_pp.iloc[-1], "", color))
    ax.set_ylim(0, 100); ax.set_xlim(first - 0.3, latest + 0.3)
    ax.set_xticks(range(first, latest + 1))
    ax.legend(frameon=False, fontsize=8, loc="upper right", labelcolor=INK, ncol=3)
    _axes_style(ax, "Gap between 18–39 and 60+ (percentage points)")

    CHART_DIR.mkdir(parents=True, exist_ok=True)
    out = CHART_DIR.parent / "dashboard.png"
    fig.savefig(out, dpi=150, facecolor=SURFACE)
    print(f"Saved {out}")


if __name__ == "__main__":
    main()
