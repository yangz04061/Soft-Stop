import pandas as pd
import re
from pathlib import Path

work_dir = Path(__file__).parent
req_file = work_dir / "cubiX-SGMW - System Requirements.xlsx"
df_req = pd.read_excel(req_file, sheet_name=0)

print("=" * 100)
print("VERIFICATION: Rows with replacements")
print("=" * 100)

rows_to_check = [14, 18, 19, 36]  # 0-indexed

for row_idx in rows_to_check:
    if row_idx < len(df_req):
        print(f"\nRow {row_idx + 1}:")
        print("-" * 100)
        
        # Show Summary
        if 'Summary' in df_req.columns:
            summary = str(df_req.iloc[row_idx]['Summary'])
            print(f"Summary: {summary[:80]}")
        
        # Show Description signals
        if 'Description' in df_req.columns:
            desc = str(df_req.iloc[row_idx]['Description'])
            signals = re.findall(r'\{([^}]+)\}', desc)
            if signals:
                print(f"Signals in Description ({len(signals)} total):")
                for sig in signals:
                    print(f"  - {sig}")
            else:
                print("No signals found in Description")

print("\n" + "=" * 100)
print("✓ Verification complete!")
