from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / 'data'
PROCESSED_DIR = DATA_DIR / 'processed'
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
RAW_PATH = DATA_DIR / 'raw_transactions.csv'

sns.set(style='whitegrid', palette='muted')
raw = pd.read_csv(RAW_PATH, parse_dates=['timestamp'])

plt.figure(figsize=(9, 5))
sns.countplot(data=raw, x='type', hue='is_fraud')
plt.title('Transaction Type vs Fraud')
plt.tight_layout()
plt.savefig(PROCESSED_DIR / 'transaction_type_fraud.png')
plt.close()

plt.figure(figsize=(9, 5))
sns.histplot(data=raw, x='amount', hue='is_fraud', bins=50, element='step', stat='density')
plt.title('Transaction Amount Distribution by Fraud Label')
plt.tight_layout()
plt.savefig(PROCESSED_DIR / 'amount_distribution.png')
plt.close()

correlation = raw.select_dtypes(include=['float64', 'int64']).corr()
correlation.to_csv(PROCESSED_DIR / 'correlation_matrix.csv')

print(f'EDA outputs saved in {PROCESSED_DIR}')
