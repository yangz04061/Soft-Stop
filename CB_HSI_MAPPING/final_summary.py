import pandas as pd
import re
from pathlib import Path

work_dir = Path(__file__).parent
req_file = work_dir / "cubiX-SGMW - System Requirements.xlsx"
df_req = pd.read_excel(req_file, sheet_name=0)

print("=" * 100)
print("FINAL REPLACEMENT SUMMARY")
print("=" * 100)

# Read mapping reference
ext_file = work_dir / "SGMW_external_interface_to_Kun_20260407.xlsx"
xl_ext = pd.ExcelFile(ext_file)

# Merge all sheets
all_data = []
for sheet_name in xl_ext.sheet_names:
    try:
        df_sheet = pd.read_excel(ext_file, sheet_name=sheet_name)
        if 'SGMW Ext. Interface Name' in df_sheet.columns:
            all_data.append(df_sheet)
    except:
        pass

df_ext = pd.concat(all_data, ignore_index=True)

# Create list of known SGMW Ext. Interface Names (original signal names)
original_signals = set()
for val in df_ext['SGMW Ext. Interface Name'].unique():
    if pd.notna(val):
        original_signals.add(str(val).strip())

total_rows = len(df_req)
fully_replaced_count = 0
partially_replaced_count = 0
not_replaced_count = 0

replaced_signals = set()
unreplaced_signals = set()

for row_idx in range(total_rows):
    if pd.isna(df_req.iloc[row_idx]['Description']):
        not_replaced_count += 1
        continue
    
    desc = str(df_req.iloc[row_idx]['Description'])
    signals = re.findall(r'\{([^}]+)\}', desc)
    
    if not signals:
        not_replaced_count += 1
        continue
    
    # Check how many signals are original (need replacement) vs new (already replaced)
    has_original = False
    has_new = False
    
    for sig in signals:
        # Clean signal name
        cleaned = sig.rstrip('~').strip()
        
        # Check if it's an original SGMW signal or an S_ signal (replacement)
        if cleaned.startswith('S_'):
            has_new = True
            replaced_signals.add(sig)
        elif cleaned in original_signals or cleaned[:-3] in original_signals:  # Check with _FD variant
            has_original = True
            unreplaced_signals.add(sig)
    
    if has_original and not has_new:
        not_replaced_count += 1
    elif has_original and has_new:
        partially_replaced_count += 1
    elif has_new and not has_original:
        fully_replaced_count += 1
    else:
        not_replaced_count += 1

print(f"\nTotal rows in table: {total_rows}")
print(f"\nRows with Description column:")
print(f"  - Fully replaced (all signals are HSI names): {fully_replaced_count}")
print(f"  - Partially replaced (mix of original and HSI): {partially_replaced_count}")
print(f"  - Not replaced (still using original names): {not_replaced_count}")
print(f"\nSuccessfully replaced signals (S_ format): {len(replaced_signals)}")
print(f"Unreplaced signals (original format): {len(unreplaced_signals)}")

# Show some examples
print("\n" + "=" * 100)
print("EXAMPLES OF REPLACED SIGNALS (showing in Description):")
print("=" * 100)
for sig in sorted(replaced_signals)[:10]:
    print(f"  {sig}")

print("\n" + "=" * 100)
print("EXAMPLES OF UNREPLACED SIGNALS (still need replacement):")
print("=" * 100)
for sig in sorted(unreplaced_signals)[:10]:
    print(f"  {sig}")

# Save summary
summary_file = work_dir / "replacement_summary.txt"
with open(summary_file, 'w', encoding='utf-8') as f:
    f.write("REPLACEMENT STATUS SUMMARY\n")
    f.write("=" * 100 + "\n\n")
    f.write(f"Total rows: {total_rows}\n\n")
    f.write(f"Fully replaced rows: {fully_replaced_count}\n")
    f.write(f"Partially replaced rows: {partially_replaced_count}\n")
    f.write(f"Not replaced rows: {not_replaced_count}\n\n")
    f.write(f"Successfully replaced signals: {len(replaced_signals)}\n")
    f.write(f"Unreplaced signals: {len(unreplaced_signals)}\n")

print(f"\nSummary saved to: {summary_file}")
