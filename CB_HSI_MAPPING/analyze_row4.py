import pandas as pd
import re
from pathlib import Path

work_dir = Path(__file__).parent
req_file = work_dir / "cubiX-SGMW - System Requirements.xlsx"
df_req = pd.read_excel(req_file, sheet_name=0)

print("=" * 100)
print("ANALYZING ROW 4 (Index 3)")
print("=" * 100)

if len(df_req) >= 4:
    row_idx = 3  # Row 4 (0-indexed)
    row_4 = df_req.iloc[row_idx]
    
    print(f"\nRow 4 Summary: {row_4.get('Summary', 'N/A')}")
    
    if 'Description' in df_req.columns:
        desc = str(row_4['Description'])
        print(f"\nDescription column length: {len(desc)} characters")
        print(f"\nFirst 1000 characters:")
        print("-" * 100)
        print(desc[:1000])
        print("-" * 100)
        
        # Find all {} patterns
        all_brackets = re.findall(r'\{[^}]*\}', desc)
        print(f"\nAll bracket patterns found ({len(all_brackets)} total):")
        for i, bracket in enumerate(all_brackets, 1):
            print(f"{i}. '{bracket}'")
            # Show character codes to detect spaces
            print(f"   Hex: {bracket.encode().hex()}")
        
        # Try different regex patterns
        print(f"\n" + "=" * 100)
        print("TESTING DIFFERENT EXTRACTION PATTERNS:")
        print("=" * 100)
        
        # Pattern 1: Original
        signals_1 = re.findall(r'\{([^}]+)\}', desc)
        print(f"\nPattern 1 - standard extraction: {len(signals_1)} matches")
        for sig in signals_1:
            print(f"  - '{sig}'")
        
        # Pattern 2: With strip
        signals_2 = re.findall(r'\{\s*([^}]+)\s*\}', desc)
        print(f"\nPattern 2 - with space handling: {len(signals_2)} matches")
        for sig in signals_2:
            print(f"  - '{sig}'")
            print(f"    Stripped: '{sig.strip()}'")

else:
    print(f"Table has only {len(df_req)} rows")
