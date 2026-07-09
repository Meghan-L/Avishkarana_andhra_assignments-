from pathlib import Path
import pandas as pd
import streamlit as st
import altair as alt

ROOT = Path(__file__).resolve().parent
RAW_PATH = ROOT / "data" / "raw_data.csv"
FACT_PATH = ROOT / "data" / "processed" / "Fact_Posts.csv"
SQL_PATH = ROOT / "database" / "queries.sql"
INSIGHTS_PATH = ROOT / "dashboard" / "executive_insights.md"


@st.cache_data
def load_data() -> pd.DataFrame:
    if not FACT_PATH.exists():
        st.error("Processed data not found. Run the pipeline first.")
        st.stop()
    df = pd.read_csv(FACT_PATH, parse_dates=["Timestamp"])
    df["Date"] = pd.to_datetime(df["Timestamp"]).dt.date
    return df


@st.cache_data
def load_sql() -> str:
    if SQL_PATH.exists():
        return SQL_PATH.read_text(encoding="utf-8")
    return "SQL file not available."


@st.cache_data
def load_insights() -> str:
    if INSIGHTS_PATH.exists():
        return INSIGHTS_PATH.read_text(encoding="utf-8")
    return "Executive insights not available."


def build_hashtag_table(df: pd.DataFrame) -> pd.DataFrame:
    hashtags = df["Hashtags"].dropna().astype(str).str.split(" ")
    exploded = hashtags.explode().to_frame("Hashtag")
    exploded["Hashtag"] = exploded["Hashtag"].str.strip()
    exploded = exploded[exploded["Hashtag"] != ""]
    exploded = exploded.groupby("Hashtag").size().reset_index(name="Count")
    exploded = exploded.sort_values(by="Count", ascending=False).head(12)
    return exploded


def header_section():
    st.set_page_config(page_title="Social Media Trend Analysis", layout="wide")
    st.title("Social Media Trend Analysis")
    st.markdown(
        "This interactive Streamlit dashboard presents the full project pipeline, 
        including data generation, cleaning, SQL analysis, visual insights, and executive strategy.")


def metrics_section(df: pd.DataFrame):
    total_posts = len(df)
    avg_engagement = df["Engagement_Score"].mean()
    sentiment_counts = df["Sentiment_Label"].value_counts(normalize=True) * 100
    positive = sentiment_counts.get("Positive", 0.0)
    negative = sentiment_counts.get("Negative", 0.0)
    neutral = sentiment_counts.get("Neutral", 0.0)

    st.subheader("Performance Overview")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Posts", f"{total_posts:,}")
    c2.metric("Avg. Engagement", f"{avg_engagement:.1f}")
    c3.metric("Positive Sentiment", f"{positive:.1f}%")
    c4.metric("Negative Sentiment", f"{negative:.1f}%")

    st.markdown(
        f"**Neutral sentiment:** {neutral:.1f}%  
        This data supports platform-specific targeting and rapid reputation monitoring.")


def charts_section(df: pd.DataFrame):
    st.subheader("Engagement Insights")
    platform_summary = df.groupby("Platform")["Engagement_Score"].sum().reset_index()
    sentiment_summary = df["Sentiment_Label"].value_counts().reset_index()
    sentiment_summary.columns = ["Sentiment", "Count"]
    weekly_trend = (
        df.groupby(["Date", "Platform"])["Engagement_Score"]
        .sum()
        .reset_index()
        .rename(columns={"Date": "date"})
    )
    hashtag_table = build_hashtag_table(df)

    col1, col2 = st.columns((2, 1))
    with col1:
        chart = alt.Chart(platform_summary).mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6).encode(
            x=alt.X("Platform:N", sort="-y"),
            y=alt.Y("Engagement_Score:Q", title="Total Engagement"),
            color=alt.Color("Platform:N", legend=None)
        ).properties(height=360)
        st.altair_chart(chart, use_container_width=True)
    with col2:
        pie = alt.Chart(sentiment_summary).mark_arc(innerRadius=50).encode(
            theta=alt.Theta(field="Count", type="quantitative"),
            color=alt.Color(field="Sentiment", type="nominal", legend=alt.Legend(title="Sentiment")),
            tooltip=["Sentiment", "Count"]
        ).properties(height=360)
        st.altair_chart(pie, use_container_width=True)

    st.markdown("---")
    st.markdown("### Weekly Engagement Trend by Platform")
    line = alt.Chart(weekly_trend).mark_line(point=True).encode(
        x=alt.X("date:T", title="Date"),
        y=alt.Y("Engagement_Score:Q", title="Engagement Score"),
        color=alt.Color("Platform:N", title="Platform"),
        tooltip=["date", "Platform", "Engagement_Score"]
    ).interactive()
    st.altair_chart(line, use_container_width=True)

    st.markdown("---")
    st.subheader("Top Hashtags")
    st.table(hashtag_table)


def data_section(df: pd.DataFrame):
    st.subheader("Data Preview")
    st.dataframe(df.sample(10), use_container_width=True)
    st.markdown("### Quick Metrics")
    st.write(df.describe(include="all"))


def documentation_section():
    st.subheader("Project Documents")
    st.markdown("#### SQL analysis")
    st.code(load_sql(), language="sql")
    st.markdown("#### Executive Insights")
    st.markdown(load_insights())


def main():
    header_section()
    df = load_data()
    metrics_section(df)
    charts_section(df)
    data_section(df)
    documentation_section()


if __name__ == "__main__":
    main()
