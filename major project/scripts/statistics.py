from pathlib import Path
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
FACT_PATH = ROOT / "data" / "processed" / "Fact_Posts.csv"
OUTPUT_PATH = ROOT / "data" / "processed" / "statistical_summary.txt"


def run_statistics() -> None:
    df = pd.read_csv(FACT_PATH, parse_dates=["Timestamp"])
    platform_groups = [df.loc[df["Platform"] == platform, "Engagement_Score"] for platform in sorted(df["Platform"].unique())]
    anova_result = stats.f_oneway(*platform_groups)

    df["Posting_Window"] = df["Timestamp"].dt.hour.apply(lambda hour: "Morning" if hour < 12 else "Evening")
    morning = df.loc[df["Posting_Window"] == "Morning", "Engagement_Score"]
    evening = df.loc[df["Posting_Window"] == "Evening", "Engagement_Score"]
    ttest_result = stats.ttest_ind(morning, evening, equal_var=False)

    summary = f"""Platform Engagement ANOVA
P-value: {anova_result.pvalue:.6f}
Significant difference: {'Yes' if anova_result.pvalue < 0.05 else 'No'}

Posting Time T-Test
P-value: {ttest_result.pvalue:.6f}
Significant difference: {'Yes' if ttest_result.pvalue < 0.05 else 'No'}
"""

    OUTPUT_PATH.write_text(summary, encoding="utf-8")
    print(summary)


if __name__ == "__main__":
    run_statistics()
