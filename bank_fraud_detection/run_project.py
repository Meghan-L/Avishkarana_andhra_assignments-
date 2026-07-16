from pathlib import Path
import subprocess
import sys

BASE_DIR = Path(__file__).resolve().parent

scripts = [
    BASE_DIR / 'scripts' / 'generate_data.py',
    BASE_DIR / 'scripts' / 'clean_data.py',
    BASE_DIR / 'scripts' / 'eda.py',
    BASE_DIR / 'scripts' / 'statistics_report.py',
]

for script in scripts:
    print(f'Running {script.relative_to(BASE_DIR)}...')
    subprocess.run([sys.executable, str(script)], cwd=BASE_DIR, check=True)

print('\nProject run completed successfully.')
