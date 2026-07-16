from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / 'data'
PROCESSED_DIR = DATA_DIR / 'processed'
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
RAW_PATH = DATA_DIR / 'raw_transactions.csv'

raw = pd.read_csv(RAW_PATH, parse_dates=['timestamp'])
raw['hour'] = raw['timestamp'].dt.hour
raw['day_of_week'] = raw['timestamp'].dt.day_name()
raw['week_of_year'] = raw['timestamp'].dt.isocalendar().week

raw['high_amount'] = (raw['amount'] > 1000).astype(int)
raw['odd_hour'] = raw['hour'].isin([0, 1, 2, 3, 4, 23]).astype(int)
raw['merchant_risk'] = raw['merchant_category'].map({
    'electronics': 1,
    'grocery': 0,
    'travel': 1,
    'entertainment': 1,
    'utilities': 0,
    'healthcare': 0,
})

raw.to_csv(PROCESSED_DIR / 'clean_transactions.csv', index=False)

user_dim = raw[['customer_id']].drop_duplicates().reset_index(drop=True)
user_dim['customer_risk'] = user_dim['customer_id'].apply(lambda x: 1 if int(x.split('_')[1]) % 13 == 0 else 0)
user_dim.to_csv(PROCESSED_DIR / 'dim_customers.csv', index=False)

txn_fact = raw[['transaction_id', 'customer_id', 'timestamp', 'type', 'merchant_category', 'amount', 'is_fraud', 'high_amount', 'odd_hour', 'merchant_risk']]
txn_fact.to_csv(PROCESSED_DIR / 'fact_transactions.csv', index=False)

print(f'Cleaned data saved to {PROCESSED_DIR / "clean_transactions.csv"}')
print(f'Customer and transaction tables saved under {PROCESSED_DIR}')
