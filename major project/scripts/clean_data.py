import re
from pathlib import Path
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = ROOT / "data" / "raw_data.csv"
PROCESSED_DIR = ROOT / "data" / "processed"


def clean_text(text: str) -> str:
    if pd.isna(text):
        return "No content available"
    text = re.sub(r"https?://\S+|www\.\S+", "", str(text))
    text = re.sub(r"[^A-Za-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text or "No content available"


def build_processed_tables() -> None:
    df = pd.read_csv(RAW_PATH, parse_dates=["Timestamp"])
    df["Text_Content"] = df["Text_Content"].apply(clean_text)
    df["Hashtags"] = df["Hashtags"].fillna("#general")
    df["Likes"] = pd.to_numeric(df["Likes"], errors="coerce").fillna(0).astype(int)
    df["Shares"] = pd.to_numeric(df["Shares"], errors="coerce").fillna(0).astype(int)
    df["Comments"] = pd.to_numeric(df["Comments"], errors="coerce").fillna(0).astype(int)
    df["Sentiment_Label"] = df["Sentiment_Label"].fillna("Neutral")
    df["Username"] = df["Username"].fillna("unknown_user")
    df["Platform"] = df["Platform"].fillna("X")
    df["Engagement_Score"] = df["Likes"] + 2 * df["Comments"] + 3 * df["Shares"]

    user_map = {username: f"U{i:04d}" for i, username in enumerate(df["Username"].drop_duplicates(), start=1)}
    df["User_ID"] = df["Username"].map(user_map)

    dim_users = pd.DataFrame({
        "User_ID": list(user_map.values()),
        "Username": list(user_map.keys()),
        "Platform": df.groupby("Username")["Platform"].first().reindex(list(user_map.keys())).tolist(),
    })

    df["Date"] = df["Timestamp"].dt.strftime("%Y-%m-%d")
    df["Hour"] = df["Timestamp"].dt.hour
    df["Day_Of_Week"] = df["Timestamp"].dt.day_name()
    df["Month"] = df["Timestamp"].dt.month_name()
    df["Week_Number"] = df["Timestamp"].dt.isocalendar().week.astype(int)
    df["Time_ID"] = df["Timestamp"].dt.strftime("%Y%m%d%H")

    dim_time = df[["Time_ID", "Timestamp", "Date", "Hour", "Day_Of_Week", "Month", "Week_Number"]].drop_duplicates()
    fact_posts = df[[
        "Post_ID", "User_ID", "Time_ID", "Platform", "Timestamp", "Text_Content", "Hashtags",
        "Likes", "Shares", "Comments", "Sentiment_Label", "Engagement_Score"
    ]].copy()

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    fact_posts.to_csv(PROCESSED_DIR / "Fact_Posts.csv", index=False)
    dim_users.to_csv(PROCESSED_DIR / "Dim_Users.csv", index=False)
    dim_time.to_csv(PROCESSED_DIR / "Dim_Time.csv", index=False)
    df[["Post_ID", "User_ID", "Time_ID", "Platform", "Timestamp", "Text_Content", "Hashtags", "Likes", "Shares", "Comments", "Sentiment_Label", "Engagement_Score"]].to_csv(PROCESSED_DIR / "Cleaned_Posts.csv", index=False)

    print("Processed tables exported to", PROCESSED_DIR)


if __name__ == "__main__":
    build_processed_tables()
