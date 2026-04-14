import pandas as pd
import re
from pathlib import Path

base = Path(__file__).parent
req = pd.read_excel(base / 'cubiX-SGMW - System Requirements.xlsx', sheet_name='System Requirements')
row = 15

desc = req.at[row, 'Description']
print('Row num', row + 1)
print('Type', type(desc))
print('Len', len(desc) if isinstance(desc, str) else 'NA')
print('---')
print(str(desc)[:1000])
print('--- bracket count', len(re.findall(r'\{([^}]*)\}', str(desc))))
br = re.findall(r'\{([^}]*)\}', str(desc))
for i, b in enumerate(br, 1):
    print(f'{i}: {repr(b)[:200]}')
print('--- extract')
for i, b in enumerate(br, 1):
    matches = re.findall(r'(__[A-Za-z0-9_~]+)', b)
    print(i, matches)
