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
print("System Requirements Table - Row 17")
print("=" * 100)

if len(df_req) >= 17:
    row_17 = df_req.iloc[16]  # index 16 = row 17
    
    # Get Description column
    if 'Description' in df_req.columns:
        desc = str(row_17['Description'])
        print("\nDescription column content (first 500 chars):")
        print("=" * 100)
        print(desc[:500] + "...")
        
        # Extract content within {}
        signals_in_brackets = re.findall(r'\{([^}]+)\}', desc)
        print("\n" + "=" * 100)
        print("Signals extracted from {} in Description:")
        print("=" * 100)
        for i, signal in enumerate(signals_in_brackets, 1):
            print(f"{i}. '{signal}'")
        
        # Clean signal names (remove trailing ~)
        cleaned_signals = []
        for signal in signals_in_brackets:
            cleaned = signal.rstrip('~').strip()
            cleaned_signals.append(cleaned)
            print(f"   Cleaned: '{cleaned}'")
        
        # Find corresponding relationships in SGMW_external_interface_to_Kun_20260407
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
        
        df_ext_combined = pd.concat(all_data, ignore_index=True)
        
        # Create mapping
        print("\n" + "=" * 100)
        print("Signal replacement mapping:")
        print("=" * 100)
        
        replacements = {}
        for i, (original_signal, cleaned_signal) in enumerate(zip(signals_in_brackets, cleaned_signals)):
            match = df_ext_combined[df_ext_combined['SGMW Ext. Interface Name'] == cleaned_signal]
            if not match.empty and 'Match_HSI_Signal' in match.columns:
                hsi_signal = match.iloc[0]['Match_HSI_Signal']
                replacements[original_signal] = hsi_signal
                print(f"{i+1}. {original_signal} ({cleaned_signal}) -> {hsi_signal}")
            else:
                # Try without the _FD suffix if it has one
                if cleaned_signal.endswith('_FD'):
                    alt_signal = cleaned_signal[:-3]
                    match = df_ext_combined[df_ext_combined['SGMW Ext. Interface Name'] == alt_signal]
                    if not match.empty and 'Match_HSI_Signal' in match.columns:
                        hsi_signal = match.iloc[0]['Match_HSI_Signal']
                        replacements[original_signal] = hsi_signal
                        print(f"{i+1}. {original_signal} ({cleaned_signal}) -> {hsi_signal} (using alternative name {alt_signal})")
                    else:
                        print(f"{i+1}. WARNING: {original_signal} ({cleaned_signal}) -> No matching relationship found")
                else:
                    print(f"{i+1}. WARNING: {original_signal} ({cleaned_signal}) -> No matching relationship found")
        
        # Generate replaced description text
        print("\n" + "=" * 100)
        print("Description content after replacement:")
        print("=" * 100)
        new_desc = desc
        for old_signal, new_signal in replacements.items():
            new_desc = new_desc.replace(f"{{{old_signal}}}", f"{{{new_signal}}}")
        print(new_desc[:500] + "...")
        
        # Save results to file
        results_file = work_dir / "replacement_results.txt"
        with open(results_file, 'w', encoding='utf-8') as f:
            f.write("SIGNAL REPLACEMENT MAPPING\n")
            f.write("=" * 100 + "\n\n")
            for old_signal, new_signal in replacements.items():
                f.write(f"Old: {old_signal}\n")
                f.write(f"New: {new_signal}\n\n")
            f.write("\n" + "=" * 100 + "\n")
            f.write("REPLACED DESCRIPTION:\n")
            f.write("=" * 100 + "\n")
            f.write(new_desc)
        
        print(f"\nResults saved to: {results_file}")

else:
    print(f"Table has only {len(df_req)} rows")
