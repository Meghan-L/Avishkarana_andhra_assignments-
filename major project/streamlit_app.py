from pathlib import Path
import pandas as pd
import streamlit as st
import altair as alt

ROOT = Path(__file__).resolve().parent
FACT_PATH = ROOT / "data" / "processed" / "Fact_Posts.csv"
SQL_PATH = ROOT / "database" / "queries.sql"
INSIGHTS_PATH = ROOT / "dashboard" / "executive_insights.md"
TECH_STACK_PATH = ROOT / "dashboard" / "tech_stack.md"
WORKFLOW_PATH = ROOT / "dashboard" / "workflow_architecture.md"
CONTENT_PATH = ROOT / "dashboard" / "content_strategy.md"
ARCHITECTURE_IMAGE = ROOT / "dashboard" / "architecture_diagram.svg"
PAGES = ["Overview", "Tech Stack", "Workflow & Architecture", "Content Strategy", "Project Docs"]


@st.cache_data
def load_data() -> pd.DataFrame:
    if not FACT_PATH.exists():
        st.error("Processed data not found. Run the pipeline first.")
        st.stop()
    df = pd.read_csv(FACT_PATH, parse_dates=["Timestamp"])
    df["Date"] = pd.to_datetime(df["Timestamp"]).dt.date
    return df


@st.cache_data
def load_markdown(path: Path) -> str:
    if path.exists():
        return path.read_text(encoding="utf-8")
    return "Content not available."


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


def inject_styles() -> None:
    st.markdown(
        """
        <style>
            :root {
                --bg: #0a0515;
                --panel: #1a0f2e;
                --panel-2: #2d1b4e;
                --text: #f5edff;
                --muted: #d9b8f0;
                --accent: #9d4edd;
                --accent-2: #e0aaff;
                --border: #6a3a8f;
            }
            * {
                margin: 0;
                padding: 0;
            }
            html, body {
                background: #0a0515 !important;
                margin: 0 !important;
                padding: 0 !important;
                overflow-x: hidden;
            }
            .stApp, .main, .block-container {
                background: #0a0515 !important;
                color: var(--text) !important;
                margin: 0 !important;
                padding: 0 !important;
            }
            .stApp {
                background: linear-gradient(135deg, #1a0f2e 0%, #3d2463 45%, #2d1b4e 100%) !important;
                min-height: 100vh;
            }
            [data-testid="stAppViewContainer"], [data-testid="stAppViewContainerContent"] {
                background: #0a0515 !important;
                padding: 0 !important;
                margin: 0 !important;
            }
            [data-testid="stToolbar"], .st-emotion-cache-18ni7ap {
                display: none !important;
            }
            .st-emotion-cache-1wbqy5l, .st-emotion-cache-1y4p8pa, 
            .st-emotion-cache-bm2z3a, .st-emotion-cache-z5fcl3,
            [data-testid="stDecoration"] {
                background: transparent !important;
                padding: 0 !important;
                margin: 0 !important;
                border: none !important;
                display: none !important;
            }
            .main {
                padding-top: 0 !important;
                margin-top: 0 !important;
            }
            .block-container {
                padding-top: 0.6rem !important;
                padding-bottom: 2rem;
                max-width: 1400px;
                margin: 0 !important;
            }
            .hero-card {
                background: linear-gradient(135deg, #3d2463 0%, #7b2cbf 48%, #c77dff 100%);
                color: white;
                padding: 1.35rem 1.5rem;
                border-radius: 20px;
                box-shadow: 0 16px 40px rgba(157, 78, 221, 0.35);
                border: 1px solid rgba(255,255,255,0.18);
                margin-top: 0.15rem;
            }
            .info-card {
                background: rgba(30, 15, 46, 0.98);
                border: 1px solid var(--border);
                border-radius: 16px;
                padding: 1rem 1.1rem;
                margin-bottom: 0.85rem;
                box-shadow: 0 10px 25px rgba(157, 78, 221, 0.15);
            }
            .section-title {
                font-size: 1.08rem;
                font-weight: 700;
                color: #ffffff;
                margin-bottom: 0.2rem;
            }
            .muted {color: var(--muted);}
            .stButton > button {
                border-radius: 999px;
                border: 1px solid rgba(255,255,255,0.18);
                background: linear-gradient(135deg, #9d4edd 0%, #c77dff 100%);
                color: #ffffff;
                width: 100%;
                margin-bottom: 0.4rem;
                box-shadow: 0 10px 24px rgba(157, 78, 221, 0.32);
                transition: transform 180ms ease, box-shadow 180ms ease;
            }
            .stButton > button:hover {
                transform: translateY(-2px);
                box-shadow: 0 14px 28px rgba(157, 78, 221, 0.42);
                filter: brightness(1.05);
            }
            .stToolbar {
                background: #0a0515 !important;
            }
            [role="contentinfo"], footer {
                display: none !important;
            }
            .st-emotion-cache-18ni7ap,
            .st-emotion-cache-16txtl3,
            .st-emotion-cache-1jmvea3,
            [data-testid="stHeader"] {
                background: #0a0515 !important;
                height: 0 !important;
                padding: 0 !important;
                margin: 0 !important;
                display: none !important;
            }
            .st-emotion-cache-1wbqy5l {
                padding: 0 !important;
            }
            .viewerBadge_container__r5tak {
                display: none !important;
            }
            [data-testid="stSidebar"] {
                background: linear-gradient(180deg, #1a0f2e 0%, #2d1b4e 100%);
                border-right: 1px solid rgba(157, 78, 221, 0.12);
            }
            .stMetric {
                background: rgba(30, 15, 46, 0.98);
                border: 1px solid var(--border);
                border-radius: 14px;
                padding: 0.75rem;
                box-shadow: 0 8px 16px rgba(157, 78, 221, 0.12);
            }
            .stDataFrame, .stDataFrame div {
                background: transparent;
                color: var(--text);
            }
            h1, h2, h3, p, label, .stTextInput label, .stSelectbox label, .stMarkdown {
                color: var(--text) !important;
            }
            .stMarkdown p, .stMarkdown li {
                color: var(--muted) !important;
            }
            .stTextInput > div > div > input, .stSelectbox > div > div > div, .stTextArea textarea {
                background-color: rgba(18, 9, 31, 0.95) !important;
                color: var(--text) !important;
                border: 1px solid var(--border) !important;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def header_section() -> None:
    st.set_page_config(page_title="Social Media Intelligence Hub", layout="wide")
    inject_styles()
    st.markdown(
        """
        <style>
            .st-emotion-cache-1wbqy5l, .st-emotion-cache-1y4p8pa {
                background: transparent !important;
            }
            .st-emotion-cache-1wmy9hl {
                padding-top: 0 !important;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <div class="hero-card">
            <h1 style="margin-bottom:0.2rem;">Social Media Intelligence Hub</h1>
            <p style="margin:0; font-size:1.02rem;">A polished analytics workspace for reviewing campaign performance, architectural choices, and content planning strategy.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("")


def render_sidebar() -> str:
    if "active_page" not in st.session_state:
        st.session_state.active_page = "Overview"

    with st.sidebar:
        st.markdown("## Navigation")
        for page in PAGES:
            if st.button(page, use_container_width=True, type="primary" if st.session_state.active_page == page else "secondary"):
                st.session_state.active_page = page
                st.rerun()
        st.markdown("---")
        st.markdown("### Project snapshot")
        st.caption("Synthetic social data • Multi-platform insights • Executive-ready presentation")
    return st.session_state.active_page


def overview_page(df: pd.DataFrame) -> None:
    total_posts = len(df)
    avg_engagement = df["Engagement_Score"].mean()
    sentiment_counts = df["Sentiment_Label"].value_counts(normalize=True) * 100
    positive = sentiment_counts.get("Positive", 0.0)
    negative = sentiment_counts.get("Negative", 0.0)
    neutral = sentiment_counts.get("Neutral", 0.0)

    st.markdown("### Executive overview")
    st.markdown("<div class='info-card'><strong>Purpose:</strong> This dashboard brings together analytics findings, architecture context, and content direction so stakeholders can review the project from both a technical and business perspective.</div>", unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Posts", f"{total_posts:,}")
    c2.metric("Avg Engagement", f"{avg_engagement:.1f}")
    c3.metric("Positive Sentiment", f"{positive:.1f}%")
    c4.metric("Negative Sentiment", f"{negative:.1f}%")

    st.markdown(f"<div class='info-card'><span class='section-title'>Current view</span><br>Neutral sentiment is <strong>{neutral:.1f}%</strong>, which supports campaign balancing and rapid audience response planning.</div>", unsafe_allow_html=True)

    st.markdown("### Engagement insights")
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
        chart = (
            alt.Chart(platform_summary)
            .mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6)
            .encode(
                x=alt.X("Platform:N", sort="-y"),
                y=alt.Y("Engagement_Score:Q", title="Total Engagement"),
                color=alt.Color("Platform:N", legend=None),
            )
            .properties(height=340)
        )
        st.altair_chart(chart, use_container_width=True)
    with col2:
        pie = (
            alt.Chart(sentiment_summary)
            .mark_arc(innerRadius=50)
            .encode(
                theta=alt.Theta(field="Count", type="quantitative"),
                color=alt.Color(field="Sentiment", type="nominal", legend=alt.Legend(title="Sentiment")),
                tooltip=["Sentiment", "Count"],
            )
            .properties(height=340)
        )
        st.altair_chart(pie, use_container_width=True)

    st.markdown("### Weekly trend")
    line = (
        alt.Chart(weekly_trend)
        .mark_line(point=True)
        .encode(
            x=alt.X("date:T", title="Date"),
            y=alt.Y("Engagement_Score:Q", title="Engagement Score"),
            color=alt.Color("Platform:N", title="Platform"),
            tooltip=["date", "Platform", "Engagement_Score"],
        )
        .interactive()
    )
    st.altair_chart(line, use_container_width=True)

    st.markdown("### Top hashtags")
    st.dataframe(hashtag_table, use_container_width=True)


def tech_stack_page() -> None:
    st.markdown("### Technology stack")
    st.markdown(load_markdown(TECH_STACK_PATH))


def workflow_page() -> None:
    st.markdown("### Workflow and architecture")
    
    st.markdown(
        """
        <style>
            .flow-step {
                background: rgba(157, 78, 221, 0.16);
                border-left: 4px solid #9d4edd;
                padding: 1rem;
                margin: 1rem 0;
                border-radius: 12px;
            }
            .flow-step-title {
                font-size: 1.1rem;
                font-weight: 700;
                color: #e0aaff;
                margin-bottom: 0.3rem;
            }
            .flow-step-desc {
                color: #d9b8f0;
                font-size: 0.95rem;
                line-height: 1.5;
            }
            .flow-arrow {
                text-align: center;
                color: #9d4edd;
                font-size: 1.4rem;
                margin: 0.5rem 0;
            }
            .step-badge {
                display: inline-block;
                background: linear-gradient(135deg, #9d4edd 0%, #c77dff 100%);
                color: white;
                padding: 0.3rem 0.8rem;
                border-radius: 999px;
                font-size: 0.85rem;
                font-weight: 600;
                margin-right: 0.5rem;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )
    
    st.markdown("")
    st.markdown("#### Step-by-step execution pipeline")
    
    steps = [
        {
            "number": "1",
            "title": "Data Generation",
            "icon": "🔧",
            "description": "Synthetic social media dataset creation with 5,500 posts across multiple platforms (X, Reddit, Instagram)",
            "details": [
                "Generate randomized posts with realistic engagement metrics",
                "Distribute across platforms with realistic platform-specific patterns",
                "Assign sentiment labels (Positive, Neutral, Negative)",
                "Create hashtags and user metadata",
                "Output: raw_data.csv"
            ],
            "input": "Configuration parameters",
            "output": "raw_data.csv (5,500 rows)"
        },
        {
            "number": "2",
            "title": "Data Cleaning & Normalization",
            "icon": "🧹",
            "description": "Transform raw data into clean, normalized tables ready for analysis",
            "details": [
                "Remove duplicates and invalid entries",
                "Normalize text content and hashtags",
                "Parse timestamps into structured format",
                "Create dimensional tables (users, time)",
                "Calculate derived metrics (engagement scores)"
            ],
            "input": "raw_data.csv",
            "output": "Fact_Posts.csv, Dim_Users.csv, Dim_Time.csv"
        },
        {
            "number": "3",
            "title": "SQL Analysis",
            "icon": "📊",
            "description": "Execute analytical SQL queries to extract insights from the cleaned data",
            "details": [
                "Run platform-specific engagement queries",
                "Sentiment distribution analysis",
                "User interaction patterns",
                "Time-based trend analysis",
                "Hashtag performance metrics"
            ],
            "input": "Cleaned fact & dimension tables",
            "output": "Query results and insights"
        },
        {
            "number": "4",
            "title": "Statistical Testing",
            "icon": "📈",
            "description": "Perform statistical tests to validate hypotheses and find significant patterns",
            "details": [
                "ANOVA test for platform engagement differences",
                "T-tests for posting time impacts",
                "Correlation analysis on engagement factors",
                "Sentiment impact on metrics",
                "Confidence intervals and p-values"
            ],
            "input": "Processed data",
            "output": "Statistical summaries and p-values"
        },
        {
            "number": "5",
            "title": "Executive Dashboard",
            "icon": "🎯",
            "description": "Present findings in an interactive, professional dashboard for stakeholders",
            "details": [
                "Real-time analytics overview",
                "Interactive charts and filters",
                "Tech stack documentation",
                "Content planning recommendations",
                "Architecture and workflow reference"
            ],
            "input": "All processed results",
            "output": "Professional Streamlit dashboard"
        }
    ]
    
    for i, step in enumerate(steps):
        col1, col2 = st.columns([0.05, 0.95])
        with col1:
            st.markdown(f'<span class="step-badge">{step["number"]}</span>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="flow-step-title">{step["icon"]} {step["title"]}</div>', unsafe_allow_html=True)
        
        st.markdown(f'<div class="flow-step-desc">{step["description"]}</div>', unsafe_allow_html=True)
        
        with st.expander(f"📌 View details for Step {step['number']}", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**What happens:**")
                for detail in step["details"]:
                    st.markdown(f"• {detail}")
            with col2:
                st.markdown("**Input & Output**")
                st.markdown(f"**Input:** `{step['input']}`")
                st.markdown(f"**Output:** `{step['output']}`")
        
        if i < len(steps) - 1:
            st.markdown('<div class="flow-arrow">↓</div>', unsafe_allow_html=True)
    
    st.markdown("")
    st.markdown("---")
    st.markdown("#### System Architecture")
    if ARCHITECTURE_IMAGE.exists():
        st.image(str(ARCHITECTURE_IMAGE), use_container_width=True, caption="Complete pipeline flow")



def content_strategy_page() -> None:
    st.markdown("### Content strategy guide")
    st.markdown(load_markdown(CONTENT_PATH))


def docs_page() -> None:
    st.markdown("### Project documentation")
    st.markdown("#### SQL analysis")
    st.code(load_sql(), language="sql")
    st.markdown("#### Executive insights")
    st.markdown(load_insights())


def main() -> None:
    header_section()
    page = render_sidebar()
    df = load_data()

    if page == "Overview":
        overview_page(df)
    elif page == "Tech Stack":
        tech_stack_page()
    elif page == "Workflow & Architecture":
        workflow_page()
    elif page == "Content Strategy":
        content_strategy_page()
    else:
        docs_page()


if __name__ == "__main__":
    main()
