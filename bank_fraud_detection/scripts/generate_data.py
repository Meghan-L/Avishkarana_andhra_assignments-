import random
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd

random.seed(42)

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / 'data'
DATA_DIR.mkdir(parents=True, exist_ok=True)
RAW_PATH = DATA_DIR / 'raw_transactions.csv'

TRANSACTION_TYPES = ['payment', 'withdrawal', 'transfer', 'purchase']
MERCHANT_CATEGORIES = ['electronics', 'grocery', 'travel', 'entertainment', 'utilities', 'healthcare']

NUM_CUSTOMERS = 800
NUM_TRANSACTIONS = 9500

fraud_customer_ratio = 0.08

customers = [f'cust_{i:04d}' for i in range(1, NUM_CUSTOMERS + 1)]
fraud_customers = set(random.sample(customers, int(NUM_CUSTOMERS * fraud_customer_ratio)))

start_date = datetime(2024, 1, 1)

records = []
for tx_id in range(1, NUM_TRANSACTIONS + 1):
    customer_id = random.choice(customers)
    amount = round(random.uniform(5, 1500), 2)
    tx_type = random.choices(TRANSACTION_TYPES, weights=[0.35, 0.25, 0.2, 0.2])[0]
    merchant = random.choice(MERCHANT_CATEGORIES)
    timestamp = start_date + timedelta(minutes=random.randint(0, 60 * 24 * 180))
    is_fraud = 1 if customer_id in fraud_customers and random.random() < 0.22 else 0

    if is_fraud:
        amount *= random.uniform(1.4, 4.0)
        amount = round(min(amount, 4500), 2)

    records.append({
        'transaction_id': f'TX{tx_id:07d}',
        'customer_id': customer_id,
        'timestamp': timestamp.isoformat(),
        'type': tx_type,
        'merchant_category': merchant,
        'amount': amount,
        'is_fraud': is_fraud,
    })

raw = pd.DataFrame(records)
raw.to_csv(RAW_PATH, index=False)
print(f'Saved {RAW_PATH}:', raw.shape)
