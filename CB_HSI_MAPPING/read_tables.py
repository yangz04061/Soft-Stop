import pandas as pd
import os
from pathlib import Path

# 获取工作路径
work_dir = Path(__file__).parent

# 读取 cubiX-SGMW - System Requirements 表格
req_file = work_dir / "cubiX-SGMW - System Requirements.xlsx"
print("=" * 80)
print("读取 cubiX-SGMW - System Requirements.xlsx")
print("=" * 80)

# 读取所有sheet，找到含有描述的sheet
xl_file = pd.ExcelFile(req_file)
print(f"\n所有sheet名称: {xl_file.sheet_names}")

# 尝试读取第一个sheet
df_req = pd.read_excel(req_file, sheet_name=0)
print(f"\n表格大小: {df_req.shape}")
print(f"\n列名: {df_req.columns.tolist()}")

# 查看第17行（索引为16，因为是0-indexed）
print("\n" + "=" * 80)
print("第17行的内容:")
print("=" * 80)
if len(df_req) >= 17:
    row_17 = df_req.iloc[16]
    print(row_17)
    
    # 查看Description列
    if 'Description' in df_req.columns:
        desc = df_req.iloc[16]['Description']
        print(f"\nDescription 列内容: {desc}")
        print(f"内容类型: {type(desc)}")
else:
    print(f"表格只有 {len(df_req)} 行")

# 读取 SGMW_external_interface_to_Kun_20260407 表格
print("\n" + "=" * 80)
print("读取 SGMW_external_interface_to_Kun_20260407.xlsx")
print("=" * 80)

ext_file = work_dir / "SGMW_external_interface_to_Kun_20260407.xlsx"
xl_ext = pd.ExcelFile(ext_file)
print(f"\n所有sheet名称: {xl_ext.sheet_names}")

# 合并所有sheet中的数据
all_data = []
for sheet_name in xl_ext.sheet_names:
    print(f"\n处理sheet: {sheet_name}")
    df_sheet = pd.read_excel(ext_file, sheet_name=sheet_name)
    print(f"  列名: {df_sheet.columns.tolist()}")
    print(f"  数据行数: {len(df_sheet)}")
    
    if 'SGMW Ext. Interface Name' in df_sheet.columns:
        print(f"  包含 'SGMW Ext. Interface Name' 列")
    if 'Match_HSI_Signal' in df_sheet.columns:
        print(f"  包含 'Match_HSI_Signal' 列")
        
    all_data.append(df_sheet)

# 合并所有数据
df_ext_combined = pd.concat(all_data, ignore_index=True)
print(f"\n合并后的总数据行数: {len(df_ext_combined)}")
print(f"\n前几行数据:")
if 'SGMW Ext. Interface Name' in df_ext_combined.columns and 'Match_HSI_Signal' in df_ext_combined.columns:
    print(df_ext_combined[['SGMW Ext. Interface Name', 'Match_HSI_Signal']].head(10))
