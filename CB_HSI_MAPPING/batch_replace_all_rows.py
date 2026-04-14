import pandas as pd
import re
from pathlib import Path
import sys

# Set output encoding
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

work_dir = Path(__file__).parent

# Read System Requirements table
req_file = work_dir / "cubiX-SGMW - System Requirements.xlsx"
df_req = pd.read_excel(req_file, sheet_name=0)

print("=" * 100)
print("BATCH SIGNAL REPLACEMENT FOR ALL ROWS")
print("=" * 100)

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

# Create comprehensive mapping from SGMW Ext. Interface Name to Match_HSI_Signal
print("\nBuilding signal mapping from external interface file...")
signal_mapping = {}
for idx, row in df_ext.iterrows():
    ext_name = row['SGMW Ext. Interface Name']
    hsi_signal = row['Match_HSI_Signal']
    if pd.notna(ext_name) and pd.notna(hsi_signal):
        signal_mapping[str(ext_name).strip()] = str(hsi_signal)

print(f"Total mappings loaded: {len(signal_mapping)}")

# Function to clean signal name (remove trailing ~)
def clean_signal_name(signal):
    return signal.rstrip('~').strip()

# Process Description column for all rows
print("\n" + "=" * 100)
print("Processing all rows...")
print("=" * 100)

total_rows = len(df_req)
replacements_count = 0
rows_with_replacements = 0

for row_idx in range(total_rows):
    if pd.isna(df_req.iloc[row_idx]['Description']):
        continue
    
    desc = str(df_req.iloc[row_idx]['Description'])
    
    # Find all signals in {}
    signals_in_brackets = re.findall(r'\{([^}]+)\}', desc)
    
    if not signals_in_brackets:
        continue
    
    new_desc = desc
    row_replacements = 0
    
    for signal in signals_in_brackets:
        # Clean the signal name
        cleaned = clean_signal_name(signal)
        
        # Look for exact match first
        if cleaned in signal_mapping:
            new_signal = signal_mapping[cleaned]
            new_desc = new_desc.replace(f"{{{signal}}}", f"{{{new_signal}}}")
            row_replacements += 1
        else:
            # Try without _FD suffix
            if cleaned.endswith('_FD'):
                alt_signal = cleaned[:-3]
                if alt_signal in signal_mapping:
                    new_signal = signal_mapping[alt_signal]
                    new_desc = new_desc.replace(f"{{{signal}}}", f"{{{new_signal}}}")
                    row_replacements += 1
    
    if row_replacements > 0:
        df_req.iloc[row_idx, df_req.columns.get_loc('Description')] = new_desc
        replacements_count += row_replacements
        rows_with_replacements += 1
        print(f"Row {row_idx + 1}: {row_replacements} signal(s) replaced")

print("\n" + "=" * 100)
print("REPLACEMENT SUMMARY")
print("=" * 100)
print(f"Total rows processed: {total_rows}")
print(f"Rows with replacements: {rows_with_replacements}")
print(f"Total replacements made: {replacements_count}")

# Save updated file
output_file = req_file  # Overwrite original file
df_req.to_excel(output_file, sheet_name='System Requirements', index=False)

print(f"\n✓ File updated successfully: {output_file}")
print(f"\nAll Description columns have been updated with new signal names.")

# Generate detailed report
report_file = work_dir / "batch_replacement_report.txt"
with open(report_file, 'w', encoding='utf-8') as f:
    f.write("BATCH SIGNAL REPLACEMENT REPORT\n")
    f.write("=" * 100 + "\n\n")
    f.write(f"Total rows in table: {total_rows}\n")
    f.write(f"Rows with replacements: {rows_with_replacements}\n")
    f.write(f"Total replacements made: {replacements_count}\n\n")
    f.write("=" * 100 + "\n")
    f.write("MAPPING REFERENCE\n")
    f.write("=" * 100 + "\n\n")
    
    # Sample mappings
    sample_count = 0
    for old_sig, new_sig in list(signal_mapping.items())[:20]:
        f.write(f"{old_sig} -> {new_sig}\n")
        sample_count += 1
    
    if len(signal_mapping) > 20:
        f.write(f"\n... and {len(signal_mapping) - 20} more mappings\n")

print(f"Report saved to: {report_file}")
