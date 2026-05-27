"""
第四步 - 4.2：外观满意度指标计算（NPS）
=================================
数据来源：B5（5分非常满意 ~ 1分非常不满意）
输出：本品/竞品各自的满意者/中立者/不满意者人数与占比、NPS得分
调用时机 → SKILL.md 4.2
"""

import pandas as pd
import sys
from pathlib import Path

# 将 scripts 目录加入 sys.path，以便 import utils
sys.path.insert(0, str(Path(__file__).parent))
from utils import filter_samples, fmt_p

DATA_PATH = Path(__file__).parent.parent / "references" / "iQOO15U外观测试数据0526.xlsx"

# --- NPS 评分定义 ---
SATISFIED_SCORE = 5      # 满意者
NEUTRAL_SCORE = 4        # 中立者
# 不满意者 = 1-3 分


def calc_nps_for_group(df, group_name: str) -> dict:
    """
    计算单组（本品或竞品）的 NPS 指标。

    返回包含所有字段的 dict，可直接用于表格输出。
    """
    n = len(df)
    scores = pd.to_numeric(df["B5__1"], errors="coerce").dropna()

    sat = (scores == SATISFIED_SCORE).sum()
    neu = (scores == NEUTRAL_SCORE).sum()
    dis = ((scores >= 1) & (scores <= 3)).sum()

    sat_pct = sat / n * 100 if n > 0 else 0
    neu_pct = neu / n * 100 if n > 0 else 0
    dis_pct = dis / n * 100 if n > 0 else 0
    nps_val = sat_pct - dis_pct

    return {
        "group": group_name,
        "N": n,
        "satisfied_n": sat,
        "satisfied_pct": sat_pct,
        "neutral_n": neu,
        "neutral_pct": neu_pct,
        "dissatisfied_n": dis,
        "dissatisfied_pct": dis_pct,
        "nps": nps_val,
    }


def main():
    data = pd.read_excel(DATA_PATH, "data")

    # 筛选有效样本
    benpin = filter_samples(data, fz1_val=1, fzs9_val=1)
    jingpin = filter_samples(data, fz1_val=2, fzs9_val=4)

    if len(benpin) == 0 or len(jingpin) == 0:
        print("[ERROR] 有效样本量为 0，请检查 FZ1/FZS9 筛选条件")
        sys.exit(1)

    # 计算本品 & 竞品
    bp_result = calc_nps_for_group(benpin, "本品")
    jp_result = calc_nps_for_group(jingpin, "竞品")

    # --- 输出格式化表格 ---
    print("#### 4.2 外观满意度指标\n")
    header = "| 分组 | 总有效样本量 | 满意者人数 | 满意者占比 | 中立者人数 | 中立者占比 | 不满意者人数 | 不满意者占比 | 外观满意度得分 |"
    sep = "|------|-------------|-----------|-----------|-----------|-----------|-------------|-------------|-------------|"
    print(header)
    print(sep)
    for r in [bp_result, jp_result]:
        print(
            f"| {r['group']} | {r['N']} | {r['satisfied_n']} | {r['satisfied_pct']:.2f}% | "
            f"{r['neutral_n']} | {r['neutral_pct']:.2f}% | {r['dissatisfied_n']} | "
            f"{r['dissatisfied_pct']:.2f}% | {r['nps']:.2f}% |"
        )

    # --- 预警：样本量不符合预期 ---
    for r in [bp_result, jp_result]:
        if r["N"] not in (450, 600):
            print(f"\n[预警] {r['group']}有效样本量 N={r['N']}，与预期 (600/450) 不符，请核实。")

    return bp_result, jp_result


if __name__ == "__main__":
    main()
