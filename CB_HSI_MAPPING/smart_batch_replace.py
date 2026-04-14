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

# Function to extract clean signal names from complex bracketed content
def extract_signals_from_brackets(text):
    """
    Extract signal names from brackets that may contain CSS/HTML formatting.
    Returns list of clean signal names.
    """
    if not isinstance(text, str) or pd.isna(text):
        return []
    
    # Find all content within curly brackets
    bracket_contents = re.findall(r'\{([^}]*)\}', text)
    signals = []
    
    for content in bracket_contents:
        # Try to extract signal names that follow the pattern: __SignalName~ or __SignalName
        # Signals typically start with __ and may end with ~
        signal_matches = re.findall(r'(__[A-Za-z0-9_~]+)', content)
        
        for sig_match in signal_matches:
            # Clean up the signal
            clean_sig = sig_match.rstrip('~_').strip()
            
            # Only keep if it looks like a valid signal (contains at least one letter)
            if clean_sig and any(c.isalpha() for c in clean_sig):
                # Also try without _FD suffix for fallback
                if clean_sig not in signals:
                    signals.append(clean_sig)
    
    return signals

# Function to find best match in mapping
def find_best_match(signal_name, mapping):
    """Find signal in mapping, trying exact match and variants."""
    # Remove leading __ for cleaner comparison
    clean_name = signal_name.lstrip('_')
    
    # Try exact match first
    for key, value in mapping.items():
        try:
            key_str = str(key).strip()
            if key_str == clean_name or key_str == signal_name:
                return str(value)
        except:
            continue
    
    # Try with common suffixes stripped
    base_name = clean_name
    # Remove common suffixes: _FD, _1st, _1, etc.
    base_name_no_suffix = re.sub(r'(_FD|_1st|_[0-9]|~)$', '', clean_name)
    
    if base_name != base_name_no_suffix:
        for key, value in mapping.items():
            try:
                key_str = str(key).strip()
                # Try exact match on base name
                if key_str == base_name_no_suffix:
                    return str(value)
                # Try with _FD suffix
                if key_str == base_name_no_suffix + '_FD':
                    return str(value)
            except:
                continue
    
    # Try partial matching - base name appears in key
    for key, value in mapping.items():
        try:
            key_str = str(key).strip()
            # If the mapping key starts with the base name, it might be a match
            if key_str.startswith(base_name_no_suffix) and len(key_str) <= len(base_name_no_suffix) + 4:
                return str(value)
        except:
            continue
    
    return None

# Process all rows
print("=" * 100)
print("PROCESSING ALL ROWS")
print("=" * 100)

total_replacements = 0
updated_rows = []

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
            
            # Create replacement patterns to handle the complex bracket content
            # Replace the signal name within the brackets, preserving context
            # Escape underscores and special regex characters
            escaped_signal = re.escape(signal)
            pattern = r'\{([^}]*' + escaped_signal + r'[^}]*)\}'
            replacement = r'{' + hsi_signal + r'}'
            new_description = re.sub(pattern, replacement, new_description)
            
            replacements_made += 1
            total_replacements += 1
        else:
            print(f"  ✗ {signal} → NOT FOUND in mapping")
    
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
