import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) in sys.path:
    sys.path.remove(str(SCRIPT_DIR))

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

sys.path.insert(0, str(SCRIPT_DIR))

ROOT = Path(__file__).resolve().parents[1]
FACT_PATH = ROOT / "data" / "processed" / "Fact_Posts.csv"
OUTPUT_DIR = ROOT / "data" / "processed"


def create_visuals() -> None:
    df = pd.read_csv(FACT_PATH, parse_dates=["Timestamp"])
    numeric_cols = ["Likes", "Shares", "Comments", "Engagement_Score"]
    corr = df[numeric_cols].corr()

    plt.figure(figsize=(8, 6))
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm")
    plt.title("Engagement Correlation Matrix")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "engagement_correlation_heatmap.png", dpi=300)
    plt.close()

    daily_trend = (
        df.assign(Date=df["Timestamp"].dt.floor("D"))
        .groupby(["Date", "Platform"])["Engagement_Score"]
        .sum()
        .reset_index()
    )

    plt.figure(figsize=(10, 5))
    sns.lineplot(data=daily_trend, x="Date", y="Engagement_Score", hue="Platform")
    plt.title("Daily Engagement Trend Spikes")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "trend_spikes_timeseries.png", dpi=300)
    plt.close()

    print("EDA charts saved to", OUTPUT_DIR)


if __name__ == "__main__":
    create_visuals()
