"""
第三步：确认当前问卷设计框架
=========================
1. 读取 FZ1（目标调研机型）并打印分布，供用户确认本品/竞品是否正确
2. 读取 FZS9（机型对比题）并打印分布，供用户确认样本筛选逻辑
调用时机 → SKILL.md 第三步"确认当前问卷设计框架"
"""

import pandas as pd
from pathlib import Path

DATA_PATH = Path(__file__).parent.parent / "references" / "iQOO15U外观测试数据0526.xlsx"

# FZ1 与 FZS9 编码含义（来自 code.sheet）
FZ1_LABELS = {
    1: "iQOO 15 Ultra（本品）",
    2: "iPhone 17 Pro Max（竞品）",
}

FZS9_LABELS = {
    1: "iQOO 15 Ultra 对比 苹果17 Pro Max",
    2: "iQOO 15 Ultra 对比其他机型",
    3: "iQOO 15 Ultra 未对比任何机型",
    4: "苹果17 Pro Max 对比 iQOO 15 Ultra",
    5: "苹果17 Pro Max 对比其他机型",
    6: "苹果17 Pro Max 未对比任何机型",
}


def main():
    data = pd.read_excel(DATA_PATH, "data")

    print("=" * 60)
    print("第三步：问卷设计框架确认")
    print("=" * 60)

    # --- FZ1 ---
    print("\n>> 目标调研机型（FZ1）：")
    fz1_dist = data["FZ1"].value_counts().sort_index()
    for code, count in fz1_dist.items():
        label = FZ1_LABELS.get(code, f"未知编码{code}")
        print(f"  FZ1={code} : {label} → {count} 人")

    # --- FZS9 ---
    print("\n>> 机型对比题（FZS9）：")
    fzs9_dist = data["FZS9"].value_counts().sort_index()
    for code, count in fzs9_dist.items():
        label = FZS9_LABELS.get(code, f"未知编码{code}")
        print(f"  FZS9={code} : {label} → {count} 人")

    # --- 建议筛选方案 ---
    print("\n>> 建议有效样本筛选方案：")
    bp = data[(data["FZ1"] == 1) & (data["FZS9"] == 1)]
    jp = data[(data["FZ1"] == 2) & (data["FZS9"] == 4)]
    print(f"  本品有效样本 (FZ1=1 & FZS9=1): {len(bp)} 人")
    print(f"  竞品有效样本 (FZ1=2 & FZS9=4): {len(jp)} 人")

    # --- 结果供后续步骤使用 ---
    return {
        "benpin_n": len(bp),
        "jingpin_n": len(jp),
        "benpin_filter": "FZ1==1 & FZS9==1",
        "jingpin_filter": "FZ1==2 & FZS9==4",
    }


if __name__ == "__main__":
    main()
