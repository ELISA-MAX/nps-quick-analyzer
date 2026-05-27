"""
第一步：上传数据 & 校验结构
=======================
加载 Excel 文件，打印 sheets / 行列数 / 列名预览，供人工确认数据结构。
调用时机 → SKILL.md 第一步"上传数据"
"""

import pandas as pd
import sys
from pathlib import Path

# === 配置：数据文件路径（相对于 UR-Data-analysis 目录） ===
DATA_PATH = Path(__file__).parent.parent / "references" / "iQOO15U外观测试数据0526.xlsx"


def main():
    if not DATA_PATH.exists():
        print(f"[ERROR] 数据文件不存在: {DATA_PATH}")
        sys.exit(1)

    xls = pd.ExcelFile(DATA_PATH)
    print(f"数据文件: {DATA_PATH.name}")
    print(f"Sheets: {xls.sheet_names}")

    for sheet in xls.sheet_names:
        df = pd.read_excel(xls, sheet)
        print(f"\n--- {sheet}.sheet ---")
        print(f"  行数: {len(df)}")
        print(f"  列数: {len(df.columns)}")
        print(f"  前5列名: {list(df.columns[:5])}")
        print(f"  后5列名: {list(df.columns[-5:])}")

    # 读取 data.sheet 整体信息
    data = pd.read_excel(xls, "data")
    print(f"\n=== data.sheet 总样本量: {len(data)} ===")
    print(f"FZ1 分布:\n{data['FZ1'].value_counts().to_string()}")
    print(f"FZS9 分布:\n{data['FZS9'].value_counts().to_string()}")


if __name__ == "__main__":
    main()
