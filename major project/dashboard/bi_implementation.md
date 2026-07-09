# BI Implementation Notes

## Power BI Measures

Total Engagement =
SUM(Fact_Posts[Engagement_Score])

Engagement Growth MoM % =
VAR CurrentMonth = CALCULATE([Total Engagement], DATESINPERIOD(Dim_Time[Timestamp], MAX(Dim_Time[Timestamp]), 1, MONTH))
VAR PreviousMonth = CALCULATE([Total Engagement], DATESINPERIOD(Dim_Time[Timestamp], MAX(Dim_Time[Timestamp]) - 1, MONTH))
RETURN DIVIDE(CurrentMonth - PreviousMonth, PreviousMonth, BLANK())

Sentiment Ratio =
DIVIDE(
    CALCULATE(COUNT(Fact_Posts[Post_ID]), Fact_Posts[Sentiment_Label] = "Positive"),
    CALCULATE(COUNT(Fact_Posts[Post_ID]), Fact_Posts[Sentiment_Label] = "Negative"),
    BLANK()
)

## Recommended Visuals
- KPI cards for engagement and sentiment share
- Clustered column chart for platform engagement
- Line chart for weekly velocity and trend spikes
- Matrix visual for sentiment by topic and platform
