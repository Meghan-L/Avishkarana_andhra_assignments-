# Bank Fraud Detection

## Project Overview
This project builds a complete bank fraud detection workflow with synthetic transaction data, data cleaning, exploratory data analysis, statistical insights, and a launch-ready website.

## Structure
- `data/raw_transactions.csv` — raw synthetic transaction dataset
- `data/processed/` — cleaned and transformed outputs
- `scripts/generate_data.py` — synthetic fraud transaction generator
- `scripts/clean_data.py` — cleaning, feature engineering, and fact/dimension output
- `scripts/eda.py` — visual analysis and fraud behavior insights
- `scripts/statistics.py` — statistical results and fraud risk modeling
- `database/queries.sql` — example SQL analysis queries
- `dashboard/` — BI wireframe, implementation notes, and executive summary
- `website/` — static project landing page

## Quick Start
```bash
python run_project.py
```

This project is designed to work after being zipped and extracted, so the scripts use project-relative paths and do not depend on your current terminal location.

## Files
- `run_project.py` — runs the full workflow in order
- `scripts/generate_data.py` — synthetic fraud transaction generator
- `scripts/clean_data.py` — cleaning, feature engineering, and fact/dimension output
- `scripts/eda.py` — visual analysis and fraud behavior insights
- `scripts/statistics_report.py` — statistical results and fraud risk modeling

## Deploy
Use the instructions in `DEPLOY.md` to deploy this project on Vercel.
