"""
Training Pyramid Visualization
Generates a pyramid chart showing training load distribution across
easy (aerobic base), interval (threshold/VO2), and strength categories.

Usage:
    uv run python training_pyramid.py
    uv run python training_pyramid.py --output reports/my_pyramid.png
    uv run python training_pyramid.py --weeks 4
"""

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

REPORTS_DIR = Path("reports")
EASY_CSV = REPORTS_DIR / "easy" / "hr_improvement_analysis.csv"
INTERVAL_CSV = REPORTS_DIR / "interval" / "interval_workouts_dataset.csv"
STRENGTH_CSV = REPORTS_DIR / "strength" / "strength_endurance_sessions.csv"
DEFAULT_OUTPUT = REPORTS_DIR / "training_pyramid.png"


def load_metrics(weeks: int | None = None) -> dict:
    """Load and aggregate training metrics from each category's CSV."""
    metrics = {}
    cutoff = None
    if weeks:
        cutoff = pd.Timestamp.now(tz=None) - pd.Timedelta(weeks=weeks)

    # --- Easy ---
    if EASY_CSV.exists():
        df = pd.read_csv(EASY_CSV, parse_dates=["date"])
        df["date"] = pd.to_datetime(df["date"]).dt.tz_localize(None)
        if cutoff is not None:
            df = df[df["date"] >= cutoff]
        metrics["easy"] = {
            "sessions": len(df),
            "total_duration_min": float(df["duration_min"].sum()),
            "label": "Easy / Aerobic Base",
            "sublabel": "Zone 1–2 · Low aerobic · Long slow distance",
            "color": "#43A047",
        }
    else:
        print(f"[WARN] Not found: {EASY_CSV}")
        metrics["easy"] = {
            "sessions": 0,
            "total_duration_min": 0.0,
            "label": "Easy / Aerobic Base",
            "sublabel": "Zone 1–2 · Low aerobic · Long slow distance",
            "color": "#43A047",
        }

    # --- Interval ---
    if INTERVAL_CSV.exists():
        df = pd.read_csv(INTERVAL_CSV, parse_dates=["date"])
        df["date"] = pd.to_datetime(df["date"]).dt.tz_localize(None)
        if cutoff is not None:
            df = df[df["date"] >= cutoff]
        metrics["interval"] = {
            "sessions": len(df),
            "total_duration_min": float(df["total_workout_duration_min"].sum()),
            "label": "Interval / Threshold",
            "sublabel": "Zone 3–4 · Threshold · VO₂max intervals",
            "color": "#FB8C00",
        }
    else:
        print(f"[WARN] Not found: {INTERVAL_CSV}")
        metrics["interval"] = {
            "sessions": 0,
            "total_duration_min": 0.0,
            "label": "Interval / Threshold",
            "sublabel": "Zone 3–4 · Threshold · VO₂max intervals",
            "color": "#FB8C00",
        }

    # --- Strength ---
    if STRENGTH_CSV.exists():
        df = pd.read_csv(STRENGTH_CSV, parse_dates=["date"])
        df["date"] = pd.to_datetime(df["date"]).dt.tz_localize(None)
        if cutoff is not None:
            df = df[df["date"] >= cutoff]
        metrics["strength"] = {
            "sessions": len(df),
            "total_duration_min": float(df["duration_min"].sum()),
            "label": "Strength",
            "sublabel": "Gym · Body weight · Resistance training",
            "color": "#1E88E5",
        }
    else:
        print(f"[WARN] Not found: {STRENGTH_CSV}")
        metrics["strength"] = {
            "sessions": 0,
            "total_duration_min": 0.0,
            "label": "Strength",
            "sublabel": "Gym · Body weight · Resistance training",
            "color": "#1E88E5",
        }

    return metrics


def draw_pyramid(metrics: dict, output_path: Path = DEFAULT_OUTPUT, weeks: int | None = None) -> None:
    """Render and save the training pyramid PNG."""

    # Order: bottom = easy (base), middle = strength, top = interval
    tiers = [
        metrics["easy"],
        metrics["strength"],
        metrics["interval"],
    ]

    total_min = sum(t["total_duration_min"] for t in tiers)
    total_min_safe = total_min or 1.0

    # Heights proportional to training duration so the base visually dominates
    fracs = [t["total_duration_min"] / total_min_safe for t in tiers]

    # ── Canvas setup ─────────────────────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(11, 8))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 11)
    ax.axis("off")
    fig.patch.set_facecolor("#F5F5F5")

    # ── Pyramid geometry ─────────────────────────────────────────────────────
    # The pyramid lives between y=1 and y=9, x apex at x=5
    pyramid_bottom = 1.0
    pyramid_top = 9.0
    pyramid_height = pyramid_top - pyramid_bottom
    apex_x = 5.0
    half_base = 3.8  # half-width at the very base

    def x_bounds_at_y(y: float):
        """Left/right x at a given y; linearly taper from base to apex."""
        frac_up = (y - pyramid_bottom) / pyramid_height  # 0 = base, 1 = apex
        hw = half_base * (1.0 - frac_up)
        return apex_x - hw, apex_x + hw

    # Build y-band boundaries (bottom → top, proportional to training time)
    y_boundaries = [pyramid_bottom]
    for frac in fracs:
        y_boundaries.append(y_boundaries[-1] + frac * pyramid_height)
    # Clamp top to exact pyramid_top
    y_boundaries[-1] = pyramid_top

    # ── Draw bands ────────────────────────────────────────────────────────────
    for i, tier in enumerate(tiers):
        y_bot = y_boundaries[i]
        y_top = y_boundaries[i + 1]
        xl_bot, xr_bot = x_bounds_at_y(y_bot)
        xl_top, xr_top = x_bounds_at_y(y_top)

        poly = plt.Polygon(
            [
                [xl_bot, y_bot],
                [xr_bot, y_bot],
                [xr_top, y_top],
                [xl_top, y_top],
            ],
            closed=True,
            facecolor=tier["color"],
            edgecolor="white",
            linewidth=2.5,
            alpha=0.90,
            zorder=2,
        )
        ax.add_patch(poly)

        # ── Band label ────────────────────────────────────────────────────────
        y_mid = (y_bot + y_top) / 2
        band_height = y_top - y_bot
        pct = (tier["total_duration_min"] / total_min_safe) * 100
        hours = tier["total_duration_min"] / 60
        stats_line = f"{tier['sessions']} sessions  ·  {hours:.1f} hrs  ·  {pct:.0f}%"

        # Narrow bands: place label outside to the left with a leader line
        if band_height < 1.8:
            _, xr_mid = x_bounds_at_y(y_mid)
            label_x = 0.3
            ax.annotate(
                f"{tier['label']}\n{stats_line}",
                xy=(xr_mid, y_mid),
                xytext=(label_x, y_mid),
                ha="left",
                va="center",
                fontsize=9,
                fontweight="bold",
                color=tier["color"],
                zorder=5,
                arrowprops=dict(
                    arrowstyle="-",
                    color=tier["color"],
                    lw=1.4,
                    connectionstyle="arc3,rad=0.0",
                ),
                multialignment="left",
            )
        else:
            # Wide bands: label centred inside
            main_fontsize = max(9, min(13, band_height * 5.5))
            sub_fontsize = max(8, min(10, band_height * 4.0))
            ax.text(
                apex_x,
                y_mid + 0.15,
                tier["label"],
                ha="center",
                va="center",
                fontsize=main_fontsize,
                fontweight="bold",
                color="white",
                zorder=3,
            )
            ax.text(
                apex_x,
                y_mid - 0.35,
                stats_line,
                ha="center",
                va="center",
                fontsize=sub_fontsize,
                color="white",
                alpha=0.92,
                zorder=3,
            )

    # ── Outer pyramid outline ─────────────────────────────────────────────────
    xl_base, xr_base = x_bounds_at_y(pyramid_bottom)
    outline = plt.Polygon(
        [[xl_base, pyramid_bottom], [xr_base, pyramid_bottom], [apex_x, pyramid_top]],
        closed=True,
        fill=False,
        edgecolor="#BDBDBD",
        linewidth=1.5,
        zorder=4,
    )
    ax.add_patch(outline)

    # ── Right-side tick marks for wide bands only ─────────────────────────────
    zone_meta = [
        ("Zone 1–2", "#43A047"),
        ("Strength", "#1E88E5"),
        ("Zone 3–4", "#FB8C00"),
    ]
    for i, (zlabel, zcolor) in enumerate(zone_meta):
        y_bot = y_boundaries[i]
        y_top = y_boundaries[i + 1]
        band_height = y_top - y_bot
        if band_height < 1.8:
            continue  # narrow band already labelled on the left via annotation
        y_mid = (y_bot + y_top) / 2
        _, xr = x_bounds_at_y(y_mid)
        ax.text(
            xr + 0.25,
            y_mid,
            zlabel,
            ha="left",
            va="center",
            fontsize=9,
            color=zcolor,
            fontweight="bold",
            zorder=5,
        )
        ax.plot([xr, xr + 0.2], [y_mid, y_mid], color=zcolor, linewidth=1.5, zorder=5)

    # ── Title ─────────────────────────────────────────────────────────────────
    title = "Training Pyramid"
    if weeks:
        title += f"  (last {weeks} weeks)"
    ax.text(apex_x, 10.3, title, ha="center", va="top", fontsize=17, fontweight="bold", color="#212121")

    # ── Footer ────────────────────────────────────────────────────────────────
    footer = f"Total: {total_min / 60:.1f} hrs  ·  {sum(t['sessions'] for t in tiers)} sessions"
    if total_min == 0:
        footer = "No data found — check reports/ directory"
    ax.text(apex_x, 0.5, footer, ha="center", va="top", fontsize=10, color="#757575")

    # ── Save ──────────────────────────────────────────────────────────────────
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="#F5F5F5")
    plt.close()
    print(f"[OK] Saved → {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate a training pyramid visualization from easy, interval, and strength reports."
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Output PNG path (default: reports/training_pyramid.png)",
    )
    parser.add_argument(
        "--weeks",
        type=int,
        default=None,
        metavar="N",
        help="Limit to the last N weeks of data (default: all time)",
    )
    args = parser.parse_args()

    metrics = load_metrics(weeks=args.weeks)

    print("\nTraining Load Summary:")
    print(f"  {'Category':<12} {'Sessions':>8} {'Hours':>8} {'Share':>7}")
    print(f"  {'-'*40}")
    total_min = sum(m["total_duration_min"] for m in metrics.values()) or 1
    for key, m in metrics.items():
        pct = m["total_duration_min"] / total_min * 100
        print(f"  {key:<12} {m['sessions']:>8d} {m['total_duration_min']/60:>8.1f} {pct:>6.0f}%")
    print(f"  {'-'*40}")
    print(f"  {'TOTAL':<12} {sum(m['sessions'] for m in metrics.values()):>8d} {total_min/60:>8.1f}\n")

    draw_pyramid(metrics, output_path=args.output, weeks=args.weeks)


if __name__ == "__main__":
    main()
