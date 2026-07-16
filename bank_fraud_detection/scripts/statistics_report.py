from pathlib import Path
import pandas as pd
from scipy.stats import chi2_contingency

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / 'data'
PROCESSED_DIR = DATA_DIR / 'processed'
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
RAW_PATH = DATA_DIR / 'raw_transactions.csv'

raw = pd.read_csv(RAW_PATH)

cross_tab = pd.crosstab(raw['merchant_category'], raw['is_fraud'])
chi2, p, dof, expected = chi2_contingency(cross_tab)

with open(PROCESSED_DIR / 'statistical_summary.txt', 'w') as f:
    f.write('Fraud vs Merchant Category Chi-Square Test\n')
    f.write(f'chi2 = {chi2:.4f}\n')
    f.write(f'p-value = {p:.4f}\n')
    f.write(f'degrees of freedom = {dof}\n')
    f.write('\nCross-tabulation:\n')
    f.write(cross_tab.to_string())

print(f'Statistical summary saved to {PROCESSED_DIR / "statistical_summary.txt"}')
