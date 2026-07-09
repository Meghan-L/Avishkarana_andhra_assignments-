-- Top 10 trending hashtags by weekly engagement velocity
WITH weekly_engagement AS (
    SELECT
        DATE_TRUNC('week', CAST(Timestamp AS DATE)) AS week_start,
        TRIM(BOTH ' ' FROM x) AS hashtag,
        SUM(Engagement_Score) AS weekly_engagement
    FROM data_processed_fact_posts,
         LATERAL regexp_split_to_table(Hashtags, '\\s+') AS x
    GROUP BY 1, 2
),
ranked_velocity AS (
    SELECT
        week_start,
        hashtag,
        weekly_engagement,
        LAG(weekly_engagement) OVER (PARTITION BY hashtag ORDER BY week_start) AS previous_week_engagement,
        weekly_engagement - COALESCE(LAG(weekly_engagement) OVER (PARTITION BY hashtag ORDER BY week_start), 0) AS engagement_velocity
    FROM weekly_engagement
)
SELECT
    hashtag,
    week_start,
    weekly_engagement,
    engagement_velocity
FROM ranked_velocity
WHERE engagement_velocity IS NOT NULL
ORDER BY engagement_velocity DESC
LIMIT 10;

-- 7-day rolling average of engagement metrics per platform
SELECT
    Platform,
    CAST(Timestamp AS DATE) AS post_date,
    AVG(Likes) OVER (
        PARTITION BY Platform
        ORDER BY CAST(Timestamp AS DATE)
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) AS rolling_avg_likes,
    AVG(Comments) OVER (
        PARTITION BY Platform
        ORDER BY CAST(Timestamp AS DATE)
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) AS rolling_avg_comments,
    AVG(Shares) OVER (
        PARTITION BY Platform
        ORDER BY CAST(Timestamp AS DATE)
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) AS rolling_avg_shares,
    AVG(Engagement_Score) OVER (
        PARTITION BY Platform
        ORDER BY CAST(Timestamp AS DATE)
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) AS rolling_avg_engagement
FROM Fact_Posts
ORDER BY Platform, post_date;

-- Share of Voice for positive vs negative sentiment
SELECT
    Sentiment_Label,
    COUNT(*) AS post_count,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS share_of_voice_pct
FROM Fact_Posts
WHERE Sentiment_Label IN ('Positive', 'Negative')
GROUP BY Sentiment_Label;
