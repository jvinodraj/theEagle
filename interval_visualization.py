"""
Interval Workout Visualization
===============================
Generates performance charts for threshold/tempo/interval sessions.
Similar structure to easy-run scorecard but adapted for high-intensity metrics.
"""

from __future__ import annotations

import argparse
import logging
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DEFAULT_INTERVAL_CSV = Path("reports/interval/interval_workouts_dataset.csv")
DEFAULT_OUTPUT_DIR = Path("reports/interval")
DEFAULT_PLOT_PATH = Path("reports/interval/interval_performance_charts.png")


def _set_axis_limits(ax: Any, values: pd.Series, *, include_zero: bool = False, pad_ratio: float = 0.15) -> tuple[float, float]:
    """Set dynamic y-limits with padding; returns (low, high)."""
    clean = pd.to_numeric(values, errors="coerce").dropna()
    if clean.empty:
        low, high = (0.0, 1.0)
    else:
        low = float(clean.min())
        high = float(clean.max())
        if include_zero:
            low = min(low, 0.0)
            high = max(high, 0.0)

        span = high - low
        pad = max(0.5 if include_zero else 0.1, span * pad_ratio)
        low -= pad
        high += pad

    ax.set_ylim(low, high)
    return low, high


def load_interval_dataframe(csv_path: Path | None = None) -> pd.DataFrame:
    """Load interval workout dataset."""
    if csv_path is None:
        csv_path = DEFAULT_INTERVAL_CSV
    
    if not csv_path.exists():
        logger.warning(f"Interval CSV not found at {csv_path}")
        return pd.DataFrame()
    
    df = pd.read_csv(csv_path)
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").reset_index(drop=True)
    return df


def create_interval_plots(df: pd.DataFrame, output_path: Path | None = None) -> Path:
    """
    Create 2x2 visualization grid for interval/threshold workouts.
    
    Panel 1: Threshold Pace & HR Trend
    Panel 2: Power Fade & Cardiac Drift
    Panel 3: Training Effect (Aerobic vs Anaerobic)
    Panel 4: Pace Sustainability & Form Deterioration
    """
    if output_path is None:
        output_path = DEFAULT_PLOT_PATH
    
    if df.empty:
        logger.warning("Cannot create plots from empty dataframe")
        return output_path
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 11))
    fig.suptitle("Interval / Threshold Workout Performance", fontsize=16, fontweight="bold")
    
    x = np.arange(len(df))
    x_labels = df["date"].dt.strftime("%m-%d")
    
    # ─────────────────────────────────────────────────────────────
    # PANEL 1: Threshold Pace & HR Trend
    # ─────────────────────────────────────────────────────────────
    ax = axes[0, 0]
    
    # Pace (left axis)
    ax.plot(x, df["threshold_pace_min_per_km"], marker="o", linewidth=2.5, 
            markersize=8, color="darkblue", label="Threshold Pace")

    pace_vals = pd.to_numeric(df["threshold_pace_min_per_km"], errors="coerce")
    pace_min = pace_vals.min(skipna=True)
    pace_max = pace_vals.max(skipna=True)
    pace_span = float(pace_max - pace_min) if pd.notna(pace_min) and pd.notna(pace_max) else 0.0
    pace_pad = max(0.08, pace_span * 0.18)
    if pd.notna(pace_min) and pd.notna(pace_max):
        # Inverted pace axis: lower pace is better (shown higher in chart).
        ax.set_ylim(float(pace_max + pace_pad), float(pace_min - pace_pad))
    
    # Only label first and last pace
    for i in [0, len(df)-1]:
        pace = df["threshold_pace_min_per_km"].iloc[i]
        if pd.notna(pace):
            pace_str = f"{int(pace)}:{int((pace % 1) * 60):02d}"
            pace_offset = max(0.05, pace_span * 0.10)
            ax.text(i, pace - pace_offset, pace_str, ha="center", va="top", fontsize=9,
                fontweight="bold", color="darkblue", clip_on=True)
    
    ax.set_xlabel("Date", fontsize=10)
    ax.set_ylabel("Threshold Pace (min/km)", color="darkblue", fontsize=10)
    ax.tick_params(axis="y", labelcolor="darkblue", labelsize=9)
    ax.invert_yaxis()
    
    # HR (right axis)
    ax2 = ax.twinx()
    ax2.plot(x, df["threshold_hr_bpm"], marker="s", linewidth=2.5, markersize=8, 
            color="crimson", linestyle="--", label="Threshold HR")

    hr_vals = pd.to_numeric(df["threshold_hr_bpm"], errors="coerce")
    hr_low, hr_high = _set_axis_limits(ax2, hr_vals, include_zero=False, pad_ratio=0.20)
    hr_span = hr_high - hr_low
    
    # Only label first and last HR
    for i in [0, len(df)-1]:
        hr = df["threshold_hr_bpm"].iloc[i]
        if pd.notna(hr):
                hr_offset = max(0.8, hr_span * 0.05)
                ax2.text(i, hr + hr_offset, f"{int(hr)}", ha="center", va="bottom", fontsize=9,
                    fontweight="bold", color="crimson", clip_on=True)
    
    ax2.set_ylabel("Threshold HR (bpm)", color="crimson", fontsize=10)
    ax2.tick_params(axis="y", labelcolor="crimson", labelsize=9)

    
    ax.set_xticks(x)
    ax.set_xticklabels(x_labels, rotation=45, fontsize=9)
    ax.set_title("Threshold Pace & HR Trend", fontsize=11, fontweight="bold", pad=10)
    ax.grid(True, alpha=0.3)
    
    # Combined legend
    lines1, labels1 = ax.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax.legend(lines1 + lines2, labels1 + labels2, loc="upper left", fontsize=9)
    
    # ─────────────────────────────────────────────────────────────
    # PANEL 2: Power Fade % & Cardiac Drift
    # ─────────────────────────────────────────────────────────────
    ax = axes[0, 1]
    
    # Power Fade (left axis)
    power_fade = df["power_fade_pct"].fillna(0)
    colors_fade = ["crimson" if p > 10 else "darkorange" if p > 5 else "seagreen" 
                  for p in power_fade]
    bars1 = ax.bar(x - 0.2, power_fade, width=0.4, color=colors_fade, alpha=0.7, 
                  edgecolor="black", linewidth=0.7, label="Power Fade %")
    pf_low, pf_high = _set_axis_limits(ax, power_fade, include_zero=True, pad_ratio=0.18)
    pf_span = pf_high - pf_low
    
    # Only label outliers
    for i, p in enumerate(power_fade):
        if abs(p) > 15:
                 pf_offset = max(0.8, pf_span * 0.04)
                 ax.text(i - 0.2, p + (pf_offset if p > 0 else -pf_offset), f"{p:.0f}%", ha="center",
                     va="bottom" if p > 0 else "top", fontsize=8, fontweight="bold", clip_on=True)
    
    ax.set_ylabel("Power Fade (%)", color="darkred", fontsize=10)
    ax.tick_params(axis="y", labelcolor="darkred", labelsize=9)
    ax.axhline(0, color="black", linewidth=0.5)
    
    # Cardiac Drift (right axis)
    ax2 = ax.twinx()
    cardiac_drift = df["cardiac_drift_bpm"].fillna(0)
    colors_drift = ["crimson" if d > 20 else "darkorange" if d > 15 else "seagreen" 
                   for d in cardiac_drift]
    bars2 = ax2.bar(x + 0.2, cardiac_drift, width=0.4, color=colors_drift, alpha=0.6, 
                   edgecolor="black", linewidth=0.7, label="Cardiac Drift bpm")
    cd_low, cd_high = _set_axis_limits(ax2, cardiac_drift, include_zero=True, pad_ratio=0.20)
    cd_span = cd_high - cd_low
    
    # Only label min and max
    min_idx = cardiac_drift.idxmin() if len(cardiac_drift) > 0 else 0
    max_idx = cardiac_drift.idxmax() if len(cardiac_drift) > 0 else 0
    for i in [min_idx, max_idx]:
        if i < len(cardiac_drift):
            d = cardiac_drift.iloc[i]
            cd_offset = max(0.6, cd_span * 0.04)
            ax2.text(i + 0.2, d + cd_offset, f"{d:.0f}", ha="center", va="bottom", fontsize=8,
                fontweight="bold", clip_on=True)
    
    ax2.set_ylabel("Cardiac Drift (bpm)", color="darkred", fontsize=10)
    ax2.tick_params(axis="y", labelcolor="darkred", labelsize=9)
    
    ax.set_xticks(x)
    ax.set_xticklabels(x_labels, rotation=45, fontsize=9)
    ax.set_title("Power Fade & Cardiac Drift", fontsize=11, fontweight="bold", pad=10)
    ax.grid(True, alpha=0.3, axis="y")
    
    lines1, labels1 = ax.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax.legend(lines1 + lines2, labels1 + labels2, loc="upper left", fontsize=9)
    
    # ─────────────────────────────────────────────────────────────
    # PANEL 3: Training Effect (Aerobic vs Anaerobic)
    # ─────────────────────────────────────────────────────────────
    ax = axes[1, 0]
    
    aerobic_te = df["aerobic_training_effect"].fillna(0)
    anaerobic_te = df["anaerobic_training_effect"].fillna(0)
    
    width = 0.35
    bars1 = ax.bar(x - width/2, aerobic_te, width, label="Aerobic TE", 
                  color="steelblue", alpha=0.8, edgecolor="black", linewidth=0.7)
    bars2 = ax.bar(x + width/2, anaerobic_te, width, label="Anaerobic TE", 
                  color="crimson", alpha=0.8, edgecolor="black", linewidth=0.7)
    te_max = max(float(aerobic_te.max()), float(anaerobic_te.max())) if len(df) else 0.0
    ax.set_ylim(0, max(1.0, te_max + 0.8))
    
    # Add value labels on bars
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            if height > 0.2:
                  ax.text(bar.get_x() + bar.get_width()/2., height + 0.12,
                      f'{height:.1f}', ha='center', va='bottom', fontsize=8, fontweight="bold", clip_on=True)
    
    ax.set_xticks(x)
    ax.set_xticklabels(x_labels, rotation=45, fontsize=9)
    ax.set_ylabel("Training Effect", fontsize=10)
    ax.set_title("Training Effect (Aerobic vs Anaerobic)", fontsize=11, fontweight="bold", pad=10)
    ax.legend(loc="upper left", fontsize=9)
    ax.grid(True, alpha=0.3, axis="y")
    
    # ─────────────────────────────────────────────────────────────
    # PANEL 4: Pace Sustainability & Form Deterioration
    # ─────────────────────────────────────────────────────────────
    ax = axes[1, 1]
    
    # Pace Sustainability % (left axis)
    pace_sust = df["pace_sustainability_pct"].fillna(0)
    colors_sust = ["crimson" if p < -20 else "darkorange" if p < 0 else "seagreen" 
                  for p in pace_sust]
    ax.bar(x - 0.2, pace_sust, width=0.4, color=colors_sust, alpha=0.7, 
          edgecolor="black", linewidth=0.7, label="Pace Sustainability %")
    ps_low, ps_high = _set_axis_limits(ax, pace_sust, include_zero=True, pad_ratio=0.20)
    ps_span = ps_high - ps_low
    
    # Only label significant values
    for i, p in enumerate(pace_sust):
        if abs(p) > 30:
                 ps_offset = max(1.0, ps_span * 0.05)
                 ax.text(i - 0.2, p + (ps_offset if p >= 0 else -ps_offset), f"{p:.0f}%", ha="center",
                     va="bottom" if p >= 0 else "top", fontsize=8, fontweight="bold", clip_on=True)
    
    ax.axhline(0, color="black", linewidth=1)
    ax.set_ylabel("Pace Sustainability (%)", color="darkslategray", fontsize=10)
    ax.tick_params(axis="y", labelcolor="darkslategray", labelsize=9)
    
    # Form Deterioration (right axis)
    ax2 = ax.twinx()
    form_det = df["form_deterioration_pct"].fillna(0)
    colors_form = ["crimson" if f > 15 else "darkorange" if f > 10 else "seagreen" 
                  for f in form_det]
    ax2.scatter(x + 0.2, form_det, s=140, color=colors_form, alpha=0.7, 
               edgecolors="black", linewidth=0.7, label="Form Deterioration %", marker="D")
    fd_low, fd_high = _set_axis_limits(ax2, form_det, include_zero=True, pad_ratio=0.22)
    fd_span = fd_high - fd_low
    
    # Only label significant values
    for i, f in enumerate(form_det):
        if f > 12 or f < -5:
                fd_offset = max(0.8, fd_span * 0.05)
                ax2.text(i + 0.2, f + fd_offset, f"{f:.0f}%", ha="center", va="bottom", fontsize=8,
                    fontweight="bold", clip_on=True)
    
    ax2.set_ylabel("Form Deterioration (%)", color="darkslategray", fontsize=10)
    ax2.tick_params(axis="y", labelcolor="darkslategray", labelsize=9)
    
    ax.set_xticks(x)
    ax.set_xticklabels(x_labels, rotation=45, fontsize=9)
    ax.set_title("Pace Sustainability & Form", fontsize=11, fontweight="bold", pad=10)
    ax.grid(True, alpha=0.3, axis="y")
    
    lines1, labels1 = ax.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax.legend(lines1 + lines2, labels1 + labels2, loc="lower left", fontsize=9)
    
    plt.tight_layout(rect=[0, 0, 0.96, 0.95])
    fig.subplots_adjust(wspace=0.32, hspace=0.34, right=0.93)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=300)
    logger.info(f"Saved interval performance charts to {output_path}")
    plt.close(fig)
    
    return output_path


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Interval workout visualization")
    parser.add_argument(
        "--csv",
        type=Path,
        default=DEFAULT_INTERVAL_CSV,
        help="Path to interval_workouts_dataset.csv",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_PLOT_PATH,
        help="Output PNG path (default: reports/interval/interval_performance_charts.png)",
    )
    args = parser.parse_args(argv)
    
    try:
        df = load_interval_dataframe(args.csv)
        if df.empty:
            logger.error("No interval data to plot")
            return 1
        
        plot_path = create_interval_plots(df, args.output)
        logger.info(f"✓ Interval performance charts created: {plot_path}")
        return 0
    except Exception as exc:
        logger.error(f"ERROR: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
