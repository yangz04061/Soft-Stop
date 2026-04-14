import pandas as pd
import re
import sys
from pathlib import Path

# Configure UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

# Define paths
base_path = Path(__file__).parent
req_file = base_path / "cubiX-SGMW - System Requirements.xlsx"
ext_file = base_path / "SGMW_external_interface_to_Kun_20260407.xlsx"

# Read requirements table
print("Reading System Requirements table...")
req_df = pd.read_excel(req_file, sheet_name="System Requirements")
print(f"Loaded {len(req_df)} rows\n")

# Read external interface mappings
print("Reading SGMW External Interface mappings...")
ext_sheets = pd.read_excel(ext_file, sheet_name=None)
ext_dfs = [df for df in ext_sheets.values()]
ext_merged = pd.concat(ext_dfs, ignore_index=True)
print(f"Loaded {len(ext_merged)} mapping rows\n")

# Create signal mapping: SGMW Ext. Interface Name -> Match_HSI_Signal
signal_mapping = {}
for _, row in ext_merged.iterrows():
    ext_name = row.get('SGMW Ext. Interface Name', '')
    hsi_name = row.get('Match_HSI_Signal', '')
    
    # Convert to string and clean
    if pd.notna(ext_name):
        ext_name = str(ext_name).strip()
    if pd.notna(hsi_name):
        hsi_name = str(hsi_name).strip()
    
    if ext_name and hsi_name:
        signal_mapping[ext_name] = hsi_name

print(f"Created mapping with {len(signal_mapping)} signal pairs\n")

# Function to clean signal name: extract from __SignalName~_FD format
def clean_signal_name(raw_signal):
    """
    Clean signal name extracted from content.
    Raw format: __ABSAtv~_FD, __PrDrvMtrTorqMinLitVal~_FD, etc.
    Should become: ABSAtv_FD, PrDrvMtrTorqMinLitVal_FD
    """
    # Remove leading underscores
    cleaned = raw_signal.lstrip('_')
    # Remove tildes (these are formatting markers)
    cleaned = cleaned.replace('~', '')
    # Remove trailing underscores (from HTML formatting)
    cleaned = cleaned.rstrip('_')
    # Clean up extra spaces
    cleaned = cleaned.strip()
    return cleaned

# Function to extract clean signal names from complex bracketed content
def extract_signals_from_brackets(text):
    """
    Extract signal names from brackets that may contain CSS/HTML formatting.
    """
    if not isinstance(text, str) or pd.isna(text):
        return []
    
    # Find all content within curly brackets
    bracket_contents = re.findall(r'\{([^}]*)\}', text)
    signals = []
    
    for content in bracket_contents:
        # Extract anything that looks like a signal name: starting with __ 
        signal_matches = re.findall(r'(__[A-Za-z0-9_~]+)', content)
        
        for sig_match in signal_matches:
            clean_sig = clean_signal_name(sig_match)
            # Only keep if it looks like a valid signal (contains at least one letter)
            if clean_sig and any(c.isalpha() for c in clean_sig):
                if clean_sig not in signals:
                    signals.append(clean_sig)
    
    return signals

# Function to find best match in mapping
def find_best_match(signal_name, mapping):
    """Find signal in mapping with case-insensitive matching."""
    # Direct exact match (case-insensitive)
    for key, value in mapping.items():
        try:
            key_str = str(key).strip()
            if key_str.lower() == signal_name.lower():
                return str(value)
        except:
            continue
    
    return None

# Process all rows
print("=" * 100)
print("PROCESSING ALL ROWS - FINAL ATTEMPT")
print("=" * 100)

total_replacements = 0
updated_rows = []
found_unmapped = {}

for idx in req_df.index:
    description = req_df.at[idx, 'Description']
    
    if not isinstance(description, str) or pd.isna(description):
        continue
    
    # Extract signals from description
    signals = extract_signals_from_brackets(description)
    
    if not signals:
        continue
    
    print(f"\nRow {idx + 1}: Found {len(signals)} signals")
    
    replacements_made = 0
    new_description = description
    
    for signal in signals:
        # Find mapping
        hsi_signal = find_best_match(signal, signal_mapping)
        
        if hsi_signal:
            print(f"  ✓ {signal} → {hsi_signal}")
            
            # Create replacement pattern - replace signal name within brackets
            # Need to be careful with regex patterns
            escaped_signal = re.escape(signal)
            # Match: { ... signal_name ... }
            pattern = r'\{([^}]*' + escaped_signal + r'[^}]*)\}'
            replacement = r'{' + hsi_signal + r'}'
            new_description = re.sub(pattern, replacement, new_description, flags=re.IGNORECASE)
            
            replacements_made += 1
            total_replacements += 1
        else:
            print(f"  ✗ {signal} → NOT FOUND in mapping")
            if signal not in found_unmapped:
                found_unmapped[signal] = []
            found_unmapped[signal].append(idx + 1)
    
    if replacements_made > 0:
        req_df.at[idx, 'Description'] = new_description
        updated_rows.append((idx + 1, replacements_made, len(signals)))

# Save the updated file
print("\n" + "=" * 100)
print("SAVING RESULTS")
print("=" * 100)

output_file = base_path / "cubiX-SGMW - System Requirements_UPDATED.xlsx"
req_df.to_excel(output_file, sheet_name="System Requirements", index=False)
print(f"\n✓ Updated file saved to: {output_file}\n")

# Print summary
print("=" * 100)
print("SUMMARY")
print("=" * 100)
print(f"Total replacements made: {total_replacements}")
print(f"Rows updated: {len(updated_rows)}\n")

if updated_rows:
    print("Updated rows:")
    for row_num, replacements, total_signals in updated_rows:
        print(f"  Row {row_num}: {replacements}/{total_signals} signals replaced")

# Print unmapped signals for review
if found_unmapped:
    print("\n" + "=" * 100)
    print(f"UNMAPPED SIGNALS ({len(found_unmapped)} unique)")
    print("=" * 100)
    for signal in sorted(found_unmapped.keys()):
        rows_containing = found_unmapped[signal]
        print(f"  {signal:<40} (rows: {rows_containing})")
