import pandas as pd
import re
from pathlib import Path

base_path = Path(__file__).parent
ext_file = base_path / "SGMW_external_interface_to_Kun_20260407.xlsx"

# Read external interface mappings
ext_sheets = pd.read_excel(ext_file, sheet_name=None)
ext_dfs = [df for df in ext_sheets.values()]
ext_merged = pd.concat(ext_dfs, ignore_index=True)

# Get all signal names
all_signals = set()
for _, row in ext_merged.iterrows():
    ext_name = row.get('SGMW Ext. Interface Name', '')
    if pd.notna(ext_name):
        ext_name = str(ext_name).strip()
        if ext_name:
            all_signals.add(ext_name)

# Signals we're looking for from Row 4 that were marked as NOT FOUND
target_signals = [
    'ABSAtv',      # extracted as __ABSAtv~_FD
    'VSEAtv',      # extracted as __VSEAtv~_FD
    'TCSysAtv',    # extracted as __TCSysAtv~_FD
    'DragTorgCntAtv',  # extracted as __DragTorgCntAtv~_FD
    'PrDrvMtrTorqMinLitVal',  # extracted as __PrDrvMtrTorqMinLitVal~_FD
    'MCU2MtrTorqMinLitVal',   # extracted as __MCU2MtrTorqMinLitVal~_FD
    'MCU3MtrTorqMinLitVal',   # extracted as __MCU3MtrTorqMinLitVal~_FD
    'MCU4MtrTorqMinLitVal',   # extracted as __MCU4MtrTorqMinLitVal~_FD
    'VehSpdAvgDrvn',  # extracted as __VehSpdAvgDrvn~_ABS
    'VCUADASactvSts',  # extracted as __VCUADASactvSts
]

print("Searching for these signals in the mapping:")
print("=" * 100)
for target in target_signals:
    print(f"\nLooking for: {target}")
    # Look for exact matches
    matches = [s for s in all_signals if target.lower() in s.lower()]
    if matches:
        print(f"  Found {len(matches)} matches:")
        for m in sorted(matches)[:10]:  # Show first 10
            print(f"    - {m}")
        if len(matches) > 10:
            print(f"    ... and {len(matches) - 10} more")
    else:
        print(f"  No matches found")

# Now search for specific pattern variations
print("\n\n" + "=" * 100)
print("SEARCHING FOR ABS-RELATED SIGNALS")
print("=" * 100)
abs_signals = [s for s in all_signals if 'ABS' in s.upper()]
print(f"Found {len(abs_signals)} ABS-related signals:")
for s in sorted(abs_signals):
    print(f"  - {s}")

print("\n" + "=" * 100)
print("SEARCHING FOR VSE-RELATED SIGNALS")
print("=" * 100)
vse_signals = [s for s in all_signals if 'VSE' in s.upper() or 'ESC' in s.upper()]
print(f"Found {len(vse_signals)} VSE/ESC-related signals:")
for s in sorted(vse_signals):
    print(f"  - {s}")

print("\n" + "=" * 100)
print("SEARCHING FOR TORQUE-RELATED SIGNALS")
print("=" * 100)
torque_signals = [s for s in all_signals if 'TORQ' in s.upper() or 'TRQ' in s.upper()]
print(f"Found {len(torque_signals)} torque-related signals:")
for s in sorted(torque_signals)[:30]:
    print(f"  - {s}")
if len(torque_signals) > 30:
    print(f"  ... and {len(torque_signals) - 30} more")
