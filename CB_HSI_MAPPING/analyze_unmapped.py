import pandas as pd
import re
from pathlib import Path

work_dir = Path(__file__).parent

# Read SGMW external interface mapping
ext_file = work_dir / "SGMW_external_interface_to_Kun_20260407.xlsx"
xl_ext = pd.ExcelFile(ext_file)

# Merge all sheets from external interface file
all_data = []
for sheet_name in xl_ext.sheet_names:
    try:
        df_sheet = pd.read_excel(ext_file, sheet_name=sheet_name)
        if 'SGMW Ext. Interface Name' in df_sheet.columns:
            all_data.append(df_sheet)
    except:
        pass

df_ext = pd.concat(all_data, ignore_index=True)

# Create mapping
signal_mapping = {}
for idx, row in df_ext.iterrows():
    ext_name = row['SGMW Ext. Interface Name']
    hsi_signal = row['Match_HSI_Signal']
    if pd.notna(ext_name) and pd.notna(hsi_signal):
        signal_mapping[str(ext_name).strip()] = str(hsi_signal)

print("=" * 100)
print("ANALYZING UNMAPPED SIGNALS")
print("=" * 100)

# Read System Requirements
req_file = work_dir / "cubiX-SGMW - System Requirements.xlsx"
df_req = pd.read_excel(req_file, sheet_name=0)

unmapped_signals = set()
rows_with_unmapped = {}

for row_idx in range(len(df_req)):
    if pd.isna(df_req.iloc[row_idx]['Description']):
        continue
    
    desc = str(df_req.iloc[row_idx]['Description'])
    signals = re.findall(r'\{([^}]+)\}', desc)
    
    for signal in signals:
        # Clean the signal
        cleaned = signal.rstrip('~').strip()
        
        # Check if mapped
        if cleaned not in signal_mapping:
            # Try without _FD
            alt_signal = cleaned
            if cleaned.endswith('_FD'):
                alt_signal = cleaned[:-3]
            
            if alt_signal not in signal_mapping:
                unmapped_signals.add(signal)
                if row_idx + 1 not in rows_with_unmapped:
                    rows_with_unmapped[row_idx + 1] = []
                rows_with_unmapped[row_idx + 1].append(signal)

print(f"\nTotal unique unmapped signals: {len(unmapped_signals)}")
print(f"Rows with unmapped signals: {len(rows_with_unmapped)}")

print("\n" + "=" * 100)
print("UNMAPPED SIGNALS BY ROW:")
print("=" * 100)

for row_num in sorted(rows_with_unmapped.keys()):
    print(f"\nRow {row_num}:")
    for sig in sorted(set(rows_with_unmapped[row_num])):
        print(f"  - {sig}")

print("\n" + "=" * 100)
print("SEARCHING FOR SIMILAR SIGNALS IN MAPPING:")
print("=" * 100)

# For each unmapped signal, try to find similar ones
for unmapped in sorted(unmapped_signals)[:20]:  # Show first 20
    cleaned = unmapped.rstrip('~').strip()
    
    # Search for partial matches
    partial_matches = [key for key in signal_mapping.keys() if cleaned.lower() in key.lower() or key.lower() in cleaned.lower()]
    
    if partial_matches:
        print(f"\n{unmapped} (cleaned: {cleaned})")
        print(f"  Similar signals in mapping:")
        for match in partial_matches[:3]:
            print(f"    - {match} -> {signal_mapping[match][:60]}...")
    else:
        print(f"\n{unmapped} (cleaned: {cleaned})")
        print(f"  No similar signals found")

if len(unmapped_signals) > 20:
    print(f"\n... and {len(unmapped_signals) - 20} more unmapped signals")
