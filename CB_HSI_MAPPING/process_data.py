import pandas as pd
import re
from pathlib import Path
import sys

# 设置输出编码
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

work_dir = Path(__file__).parent

# 读取 System Requirements 表格
req_file = work_dir / "cubiX-SGMW - System Requirements.xlsx"
df_req = pd.read_excel(req_file, sheet_name=0)

print("=" * 100)
print("System Requirements Table - Row 17")
print("=" * 100)

if len(df_req) >= 17:
    row_17 = df_req.iloc[16]  # index 16 = row 17
    print("\nAll column values:")
    for col_name in df_req.columns:
        print(f"{col_name}: {row_17[col_name]}")
    
    # Get Description column
    if 'Description' in df_req.columns:
        desc = str(row_17['Description'])
        print("\n" + "=" * 100)
        print("Description column content:")
        print("=" * 100)
        print(desc)
        
        # Extract content within {}
        signals_in_brackets = re.findall(r'\{([^}]+)\}', desc)
        print("\n" + "=" * 100)
        print("Signals extracted from {} in Description:")
        print("=" * 100)
        for i, signal in enumerate(signals_in_brackets, 1):
            print(f"{i}. {signal}")
        
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
        for signal in signals_in_brackets:
            signal_clean = signal.strip()
            match = df_ext_combined[df_ext_combined['SGMW Ext. Interface Name'] == signal_clean]
            if not match.empty and 'Match_HSI_Signal' in match.columns:
                hsi_signal = match.iloc[0]['Match_HSI_Signal']
                replacements[signal] = hsi_signal
                print(f"{signal} -> {hsi_signal}")
            else:
                print(f"WARNING: {signal} -> No matching relationship found")
        
        # Generate replaced description text
        print("\n" + "=" * 100)
        print("Description content after replacement:")
        print("=" * 100)
        new_desc = desc
        for old_signal, new_signal in replacements.items():
            new_desc = new_desc.replace(f"{{{old_signal}}}", f"{{{new_signal}}}")
        print(new_desc)

else:
    print(f"Table has only {len(df_req)} rows")
