from pathlib import Path
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = ROOT / "data" / "raw_data.csv"


def generate_dataset(n_rows: int = 5500) -> pd.DataFrame:
    rng = np.random.default_rng(42)
    platforms = ["X", "Reddit", "Instagram"]
    platform_weights = [0.40, 0.35, 0.25]

    start = pd.Timestamp("2024-01-01")
    end = pd.Timestamp("2024-06-30 23:59:59")
    timestamps = start + pd.to_timedelta(rng.integers(0, int((end - start).total_seconds() / 3600), size=n_rows), unit="h")

    platform_series = rng.choice(platforms, size=n_rows, p=platform_weights)
    sentiment_labels = rng.choice(["Positive", "Neutral", "Negative"], size=n_rows, p=[0.38, 0.34, 0.28])

    topics = [
        "AI launch", "product update", "customer feedback", "community event", "campaign rollout",
        "market trend", "feature announcement", "brand story", "innovation spotlight", "social listening"
    ]
    verbs = ["explores", "launches", "highlights", "discusses", "celebrates", "surges", "tracks", "redefines"]
    contexts = [
        "early adoption", "user sentiment", "conversion lift", "creator engagement", "brand trust",
        "audience growth", "viral attention", "community reaction", "retention signal", "content reach"
    ]
    templates = [
        "{topic} {verb} {context} across {platform} audiences.",
        "{platform} users are reacting to {topic} as {verb} {context} in real time.",
        "The latest {topic} {verb} {context} and is reshaping how teams measure impact."
    ]

    text_contents = []
    hashtags = []
    for i in range(n_rows):
        topic = topics[rng.integers(0, len(topics))]
        verb = verbs[rng.integers(0, len(verbs))]
        context = contexts[rng.integers(0, len(contexts))]
        platform = platform_series[i]
        template = templates[rng.integers(0, len(templates))]
        content = template.format(topic=topic, verb=verb, context=context, platform=platform)
        if rng.random() < 0.65:
            content += f" {topic.lower()} is trending now."
        text_contents.append(content)

        selected_hashtags = [f"#{topic.lower().replace(' ', '')}", f"#{platform.lower()}", f"#{context.lower().replace(' ', '')}"]
        hashtags.append(" ".join(selected_hashtags[:2 + int(rng.random() < 0.5)]))

    base_likes = rng.integers(20, 1400, size=n_rows)
    base_comments = rng.integers(5, 220, size=n_rows)
    base_shares = rng.integers(1, 180, size=n_rows)

    platform_multipliers = {
        "X": {"likes": 1.10, "comments": 1.05, "shares": 1.15},
        "Reddit": {"likes": 0.95, "comments": 1.20, "shares": 1.02},
        "Instagram": {"likes": 1.25, "comments": 0.90, "shares": 1.08},
    }
    sentiment_multipliers = {
        "Positive": {"likes": 1.18, "comments": 1.10, "shares": 1.12},
        "Neutral": {"likes": 1.00, "comments": 1.00, "shares": 1.00},
        "Negative": {"likes": 0.78, "comments": 0.88, "shares": 0.82},
    }

    likes = np.round(base_likes * np.array([platform_multipliers[p]["likes"] for p in platform_series]) * np.array([sentiment_multipliers[s]["likes"] for s in sentiment_labels])).astype(int)
    comments = np.round(base_comments * np.array([platform_multipliers[p]["comments"] for p in platform_series]) * np.array([sentiment_multipliers[s]["comments"] for s in sentiment_labels])).astype(int)
    shares = np.round(base_shares * np.array([platform_multipliers[p]["shares"] for p in platform_series]) * np.array([sentiment_multipliers[s]["shares"] for s in sentiment_labels])).astype(int)

    df = pd.DataFrame(
        {
            "Timestamp": timestamps,
            "Platform": platform_series,
            "Post_ID": [f"POST_{i:05d}" for i in range(1, n_rows + 1)],
            "Username": [f"user_{rng.integers(1000, 9999)}" for _ in range(n_rows)],
            "Text_Content": text_contents,
            "Hashtags": hashtags,
            "Likes": likes,
            "Shares": shares,
            "Comments": comments,
            "Sentiment_Label": sentiment_labels,
        }
    )
    return df


if __name__ == "__main__":
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df = generate_dataset(5500)
    df.to_csv(OUTPUT_PATH, index=False)
    print(f"Generated {len(df)} rows at {OUTPUT_PATH}")
