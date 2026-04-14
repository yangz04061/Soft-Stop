import pandas as pd
import re
from pathlib import Path

work_dir = Path(__file__).parent
req_file = work_dir / "cubiX-SGMW - System Requirements.xlsx"
df_req = pd.read_excel(req_file, sheet_name=0)

print("=" * 100)
print("VERIFICATION: Row 17 Description after update")
print("=" * 100)

if len(df_req) >= 17:
    row_17 = df_req.iloc[16]
    desc = str(row_17['Description'])
    
    # Extract signals
    signals = re.findall(r'\{([^}]+)\}', desc)
    print(f"\nSignals in updated Description column:")
    for i, sig in enumerate(signals, 1):
        print(f"  {i}. {sig}")
    
    print(f"\nDescription content (showing signal placeholders):")
    print("=" * 100)
    # Show a portion with the signals
    lines = desc.split('\n')
    for line in lines:
        if '{' in line:
            print(line[:100] if len(line) > 100 else line)

print("\n✓ Update verification complete!")
