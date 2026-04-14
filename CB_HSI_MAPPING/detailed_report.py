import pandas as pd
import re
from pathlib import Path

work_dir = Path(__file__).parent
req_file = work_dir / "cubiX-SGMW - System Requirements.xlsx"
df_req = pd.read_excel(req_file, sheet_name=0)

print("=" * 100)
print("DETAILED REPLACEMENT REPORT")
print("=" * 100)

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

# Create reference set
original_signals = set()
for val in df_ext['SGMW Ext. Interface Name'].unique():
    if pd.notna(val):
        original_signals.add(str(val).strip())

replaced_rows = []
unreplaced_rows = []

for row_idx in range(len(df_req)):
    if pd.isna(df_req.iloc[row_idx]['Description']):
        continue
    
    desc = str(df_req.iloc[row_idx]['Description'])
    signals = re.findall(r'\{([^}]+)\}', desc)
    
    if not signals:
        continue
    
    row_info = {
        'row': row_idx + 1,
        'summary': df_req.iloc[row_idx].get('Summary', 'N/A'),
        'signals': signals
    }
    
    # Check if any are original or new format
    has_hsi_signal = any(str(sig).startswith('S_') for sig in signals)
    has_original_signal = any(
        (str(sig).rstrip('~').strip() in original_signals or 
         str(sig).rstrip('~').strip()[:-3] in original_signals)
        for sig in signals
    )
    
    if has_hsi_signal:
        replaced_rows.append(row_info)
    elif has_original_signal:
        unreplaced_rows.append(row_info)

print(f"\nREPLACED ROWS ({len(replaced_rows)} rows):")
print("-" * 100)
for row_info in replaced_rows:
    print(f"\nRow {row_info['row']}: {str(row_info['summary'])[:70]}")
    for sig in row_info['signals']:
        print(f"  ✓ {sig}")

print(f"\n\nUNREPLACED ROWS ({len(unreplaced_rows)} rows):")
print("-" * 100)
for row_info in unreplaced_rows[:10]:  # Show first 10
    print(f"\nRow {row_info['row']}: {str(row_info['summary'])[:70]}")
    for sig in row_info['signals']:
        print(f"  ✗ {sig}")

if len(unreplaced_rows) > 10:
    print(f"\n... and {len(unreplaced_rows) - 10} more unreplaced rows")

# Save detailed report
report_file = work_dir / "detailed_replacement_report.txt"
with open(report_file, 'w', encoding='utf-8') as f:
    f.write("DETAILED REPLACEMENT REPORT\n")
    f.write("=" * 100 + "\n\n")
    f.write(f"Total replaced rows: {len(replaced_rows)}\n")
    f.write(f"Total unreplaced rows: {len(unreplaced_rows)}\n\n")
    
    f.write("REPLACED ROWS:\n")
    f.write("-" * 100 + "\n\n")
    for row_info in replaced_rows:
        f.write(f"Row {row_info['row']}: {row_info['summary']}\n")
        for sig in row_info['signals']:
            f.write(f"  {sig}\n")
        f.write("\n")
    
    f.write("\nUNREPLACED ROWS:\n")
    f.write("-" * 100 + "\n\n")
    for row_info in unreplaced_rows:
        f.write(f"Row {row_info['row']}: {row_info['summary']}\n")
        for sig in row_info['signals']:
            f.write(f"  {sig}\n")
        f.write("\n")

print(f"\n\nDetailed report saved to: {report_file}")
print("✓ Process complete!")
