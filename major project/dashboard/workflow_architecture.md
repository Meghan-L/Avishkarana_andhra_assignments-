# Workflow and Architecture

## End-to-end pipeline
```text
Data generation
   -> Data cleaning and normalization
   -> Processed fact and dimension tables
   -> SQL analysis and reporting
   -> Exploratory insights and statistics
   -> Executive dashboard experience
```

## Architecture overview
- The raw dataset is generated first and stored as a source file.
- Cleaning scripts transform it into processed tables that are ready for analysis.
- SQL queries extract business-ready metrics from the structured tables.
- The dashboard presents the results in a professional, decision-oriented layout.

## Why this structure works
- It separates data creation from analysis and presentation.
- It makes the project easy to extend for future social-media campaigns.
- It supports both technical review and business storytelling.
