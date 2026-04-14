import pandas as pd
from pathlib import Path

work_dir = Path(__file__).parent
ext_file = work_dir / "SGMW_external_interface_to_Kun_20260407.xlsx"

# Read all sheets
xl_ext = pd.ExcelFile(ext_file)
all_data = []
for sheet_name in xl_ext.sheet_names:
    try:
        df_sheet = pd.read_excel(ext_file, sheet_name=sheet_name)
        if 'SGMW Ext. Interface Name' in df_sheet.columns:
            all_data.append(df_sheet)
    except:
        pass

df_ext = pd.concat(all_data, ignore_index=True)

# Search for signals containing "DrvShftTorq" or "PrDrv" or "ThScd"
print("Searching for related signals in SGMW interface...")
print("\n1. Signals containing 'DrvShftTorq':")
matches = df_ext[df_ext['SGMW Ext. Interface Name'].str.contains('DrvShftTorq', case=False, na=False)]
if len(matches) > 0:
    for idx, row in matches.iterrows():
        print(f"   {row['SGMW Ext. Interface Name']} -> {row['Match_HSI_Signal']}")
else:
    print("   None found")

print("\n2. Signals containing 'PrDrv':")
matches = df_ext[df_ext['SGMW Ext. Interface Name'].str.contains('PrDrv', case=False, na=False)]
if len(matches) > 0:
    for idx, row in matches.iterrows():
        print(f"   {row['SGMW Ext. Interface Name']} -> {row['Match_HSI_Signal']}")
else:
    print("   None found")

print("\n3. Signals containing 'ThScd':")
matches = df_ext[df_ext['SGMW Ext. Interface Name'].str.contains('ThScd', case=False, na=False)]
if len(matches) > 0:
    for idx, row in matches.iterrows():
        print(f"   {row['SGMW Ext. Interface Name']} -> {row['Match_HSI_Signal']}")
else:
    print("   None found")

print("\n4. Signals containing 'Torq':")
matches = df_ext[df_ext['SGMW Ext. Interface Name'].str.contains('Torq', case=False, na=False)]
if len(matches) > 0:
    for idx, row in matches.iterrows():
        print(f"   {row['SGMW Ext. Interface Name']} -> {row['Match_HSI_Signal']}")
else:
    print("   None found")

print("\n5. All unique 'SGMW Ext. Interface Name' values (first 50):")
all_signals = df_ext['SGMW Ext. Interface Name'].unique()
for i, signal in enumerate(sorted(all_signals)[:50]):
    print(f"   {signal}")
