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
print("SIGNAL REPLACEMENT PROCESS")
print("=" * 100)

# Create mapping data
mapping_data = {
    'PrDrvShftTorq~_FD~': 'S_DRIVE_ACTUAL_WHEEL_TORQUE_FRONT_AXLE',
    'ThScdDrvShftTorq~_FD~': 'S_DRIVE_ACTUAL_WHEEL_TORQUE_REAR_AXLE',
    'TMActTorq~': 'S_DRIVE_ACTUAL_WHEEL_TORQUE_FL',
    'MCU2TMActTorq~': 'S_DRIVE_ACTUAL_WHEEL_TORQUE_FR',
    'MCU3TMActTorq~': 'S_DRIVE_ACTUAL_WHEEL_TORQUE_RL',
    'MCU4TMActTorq~': 'S_DRIVE_ACTUAL_WHEEL_TORQUE_RR',
}

print("\nSignal mapping:")
for old_sig, new_sig in mapping_data.items():
    print(f"  {old_sig} -> {new_sig}")

# Get row 17 (index 16)
if len(df_req) >= 17:
    row_index = 16
    
    # Get original description
    original_desc = str(df_req.iloc[row_index]['Description'])
    
    # Perform replacement
    new_desc = original_desc
    for old_signal, new_signal in mapping_data.items():
        new_desc = new_desc.replace(f"{{{old_signal}}}", f"{{{new_signal}}}")
    
    # Update the dataframe
    df_req.iloc[row_index, df_req.columns.get_loc('Description')] = new_desc
    
    # Verify changes
    print("\nVerification:")
    print(f"  Original signals in Description:")
    orig_signals = re.findall(r'\{([^}]+)\}', original_desc)
    for sig in orig_signals:
        print(f"    - {sig}")
    
    print(f"\n  Updated signals in Description:")
    new_signals = re.findall(r'\{([^}]+)\}', new_desc)
    for sig in new_signals:
        print(f"    - {sig}")
    
    # Save updated file
    output_file = req_file  # Overwrite original file
    df_req.to_excel(output_file, sheet_name='System Requirements', index=False)
    
    print(f"\n✓ File updated successfully: {output_file}")
    print(f"\nRow 17 Description has been updated with new signal names.")
else:
    print(f"Error: Table has only {len(df_req)} rows")
