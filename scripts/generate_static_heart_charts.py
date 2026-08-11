from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

OUT_DIR = Path("reports/research")
OUT_DIR.mkdir(parents=True, exist_ok=True)


def save_weekly_training_load_chart() -> None:
    weeks = ["Base", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13"]
    tue = [427, 385, 377, 460, 429, 502, 474, 449, 350, 247, 530, 534, 367, 477]
    wed = [381, 406, 409, 463, 370, 464, 451, 389, 288, 239, 492, 469, 340, 522]
    thu = [388, 418, 447, 484, 407, 517, 502, 436, 228, 441, 544, 556, 446, 0]
    sat = [375, 383, 419, 429, 485, 522, 574, 562, 226, 637, 701, 511, 607, 0]
    sun = [337, 334, 405, 287, 440, 437, 499, 522, 218, 575, 617, 332, 544, 383]

    x = np.arange(len(weeks))

    fig, ax = plt.subplots(figsize=(12, 5), dpi=160)
    ax.bar(x, tue, label="Tue", color="#C8873A")
    ax.bar(x, wed, bottom=tue, label="Wed", color="#00D4B8")
    ax.bar(x, thu, bottom=np.array(tue) + np.array(wed), label="Thu", color="#4DB87A")
    ax.bar(
        x,
        sat,
        bottom=np.array(tue) + np.array(wed) + np.array(thu),
        label="Sat",
        color="#E05C5C",
    )
    ax.bar(
        x,
        sun,
        bottom=np.array(tue) + np.array(wed) + np.array(thu) + np.array(sat),
        label="Sun",
        color="#7C93C9",
    )

    ax.set_title("Weekly Training Load by Day (Baseline + Week 1 to 13)")
    ax.set_xlabel("Week")
    ax.set_ylabel("Training load")
    ax.set_xticks(x)
    ax.set_xticklabels(weeks)
    ax.grid(axis="y", alpha=0.2)
    ax.legend(ncol=5, frameon=False)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "weekly_training_load.png", bbox_inches="tight")
    plt.close(fig)


def save_weekly_load_focus_chart() -> None:
    weeks = ["Base", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13"]
    low = [652, 652, 902, 1036, 850, 893, 652, 660, 655, 523, 733, 753, 717, 884]
    high = [645, 645, 551, 376, 697, 729, 1048, 1129, 808, 1052, 885, 796, 1166, 770]
    ana = [46, 46, 23, 12, 24, 24, 37, 24, 12, 12, 14, 14, 14, 14]

    total = np.array(low) + np.array(high) + np.array(ana)
    low_pct = 100 * np.array(low) / total
    high_pct = 100 * np.array(high) / total
    ana_pct = 100 * np.array(ana) / total

    x = np.arange(len(weeks))

    fig, ax = plt.subplots(figsize=(12, 5), dpi=160)
    ax.stackplot(x, low_pct, high_pct, ana_pct, labels=["Low Aerobic", "High Aerobic", "Anaerobic"], colors=["#4DB87A", "#C8873A", "#E05C5C"], alpha=0.95)

    ax.set_title("Weekly Load Focus (%)")
    ax.set_xlabel("Week")
    ax.set_ylabel("Contribution (%)")
    ax.set_xticks(x)
    ax.set_xticklabels(weeks)
    ax.set_ylim(0, 100)
    ax.grid(axis="y", alpha=0.2)
    ax.legend(frameon=False, ncol=3, loc="upper center", bbox_to_anchor=(0.5, 1.12))
    fig.tight_layout()
    fig.savefig(OUT_DIR / "weekly_load_focus.png", bbox_inches="tight")
    plt.close(fig)


def save_temperature_vs_hr_chart() -> None:
    temp = np.array([
        31.135, 30.197, 30.706, 30.184, 31.541,
        30.041, 29.377, 30.709, 31.415, 31.349,
        31.470, 30.378, 30.297, 29.012, 30.678,
        29.768, 30.035, 30.997, 29.996, 30.262,
    ])
    hr = np.array([
        155, 149, 152, 152, 150,
        149, 147, 150, 151, 153,
        152, 148, 144, 146, 147,
        143, 143, 145, 143, 142,
    ])

    slope, intercept = np.polyfit(temp, hr, 1)

    fig, ax = plt.subplots(figsize=(8, 5), dpi=160)
    ax.scatter(temp, hr, color="#00D4B8", alpha=0.9, s=28)
    x_line = np.linspace(temp.min() - 0.2, temp.max() + 0.2, 100)
    y_line = slope * x_line + intercept
    ax.plot(x_line, y_line, color="#C8873A", linewidth=2)

    ax.set_title("Temperature vs Average HR (20 easy runs)")
    ax.set_xlabel("Weighted average temperature (°C)")
    ax.set_ylabel("Average HR (bpm)")
    ax.grid(alpha=0.2)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "temperature_vs_hr.png", bbox_inches="tight")
    plt.close(fig)


def save_body_composition_chart() -> None:
    labels = ["Baseline", "W2", "W3", "W4", "W5", "Current"]
    body_fat = [25.10, 25.60, 25.50, 25.00, 23.70, 23.10]
    skeletal = [42.30, 41.90, 41.90, 42.30, 43.00, 43.30]
    muscle_mass = [50.86, 51.01, 51.22, 51.49, 51.90, 51.73]
    water = [54.40, 54.60, 54.50, 55.00, 55.90, 56.30]

    x = np.arange(len(labels))

    fig, ax1 = plt.subplots(figsize=(10, 5), dpi=160)
    ax1.plot(x, body_fat, color="#E05C5C", marker="o", label="Body fat %")
    ax1.plot(x, water, color="#00D4B8", marker="o", linestyle="--", label="Body water %")
    ax1.set_ylabel("Percentage")
    ax1.set_xticks(x)
    ax1.set_xticklabels(labels)

    ax2 = ax1.twinx()
    ax2.plot(x, skeletal, color="#4DB87A", marker="o", label="Skeletal muscle (kg)")
    ax2.plot(x, muscle_mass, color="#C8873A", marker="o", label="Total muscle mass (kg)")
    ax2.set_ylabel("Mass (kg)")

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, ncol=2, frameon=False, loc="upper left")
    ax1.set_title("Body Composition Trend")
    ax1.grid(alpha=0.2)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "body_composition_trend.png", bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    save_weekly_training_load_chart()
    save_weekly_load_focus_chart()
    save_temperature_vs_hr_chart()
    save_body_composition_chart()
    print(f"Saved static charts in {OUT_DIR.resolve()}")


if __name__ == "__main__":
    main()
