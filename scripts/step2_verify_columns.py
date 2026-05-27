"""
第二步：确认数据列名称映射
=======================
从 code.sheet 提取全部题号与编码含义，建立 data.sheet 列 → 问卷语义的双向映射字典。
调用时机 → SKILL.md 第二步"确认数据列名称"
"""

import pandas as pd
import re
from pathlib import Path

DATA_PATH = Path(__file__).parent.parent / "references" / "iQOO15U外观测试数据0526.xlsx"


def build_code_mapping(filepath):
    """
    读取 code.sheet，构建 {题号: {编码: 含义}} 的完整映射。

    规则：
    - code.sheet B 列中的大写字母开头的题号与 data.sheet 列名完全一致方为映射
    - 题号后的数字编码为各选项含义
    """
    df = pd.read_excel(filepath, "code", header=None)
    questions = {}
    current_q = None

    for i in range(len(df)):
        row = df.iloc[i]
        col1 = str(row[1]).strip() if pd.notna(row[1]) else ""
        col2 = str(row[2]).strip() if pd.notna(row[2]) else ""

        # 判断是否为题号（大写字母开头 + 数字/下划线，非纯数字）
        if re.match(r"^[A-Z]+[0-9_]*[A-Z]*[0-9]*$", col1) and len(col1) >= 2 and not col1.isdigit():
            current_q = col1
            if current_q not in questions:
                questions[current_q] = {"desc": col2, "codes": {}}
        elif col1.isdigit() and current_q:
            questions[current_q]["codes"][int(col1)] = col2

    return questions


def main():
    questions = build_code_mapping(DATA_PATH)

    # 列出 SKILL 中关心的题号
    key_patterns = [
        "FZ1", "FZS9",
        "B1", "B2", "B3", "B4", "B5", "B6", "B7",
        "B8_1", "B8_2", "B9_1", "B9_2", "B10_1", "B10_2",
        "B11_1", "B11_2", "B12_1", "B12_2", "B13_1", "B13_2",
        "B14_1", "B14_2", "B15_1", "B15_2", "B16_1", "B16_2",
        "B17_1", "B17_2", "B18_1", "B18_2", "B19_1", "B19_2",
        "B20_1", "B21_1", "B21_2", "B22",
        "D1_1", "D1_3", "D2_1", "D2_3",
        "C1", "C2", "C3", "C4", "C5",
        "E1", "E2", "E3", "E4", "E5", "E6", "E7",
        "E8", "E9", "E10", "E11", "E12", "E13", "E14",
    ]

    print("=== 题号 → 编码含义映射表 ===\n")
    for kp in key_patterns:
        # 精确匹配或前缀匹配
        matches = {k: v for k, v in questions.items() if k == kp or k.startswith(kp)}
        if not matches:
            print(f"[WARN] 未找到题号: {kp}")
            continue
        for q_code, q_info in matches.items():
            print(f"[{q_code}] {q_info['desc']}")
            for code, desc in sorted(q_info["codes"].items()):
                print(f"    {code} = {desc}")
            print()

    return questions


if __name__ == "__main__":
    main()
