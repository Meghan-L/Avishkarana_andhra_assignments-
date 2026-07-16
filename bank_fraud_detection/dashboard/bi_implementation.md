# BI Implementation

The business intelligence solution should include:
- A fraud heatmap by merchant category and transaction type
- Daily transaction volume and fraud callouts
- Risk segment scoring for customers and unusual transactions
- Drill-down filters for customer, merchant, and time window

Implementation notes:
- Use the generated data tables from `data/processed`
- Leverage SQL queries for aggregate fraud insights
- Combine summary visuals with narrative insights for decision makers
