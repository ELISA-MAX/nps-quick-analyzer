"""
第四步 - 4.5：购后体验-外观维度指标计算
==================================
数据来源：
  - B6（Q1 购后满意度影响因素，多选）：请问您对这部手机的外观设计给出上述评分最主要的原因是？
  - B7（Q2 购后细项满意度，1-5量表）：具体来看，您对这些方面的满意度是？

输出：
  1. 基础样本量 N1/N2
  2. 外观影响因素（B6）占比、排名、本品 vs 竞品卡方检验
  3. 外观细项满意度（B7）平均得分、满意/中立/不满占比、排名、卡方检验

重要说明：
  B7 细项满意度分母 = 各细项自身的有效评分人数（非 B6 的 Xi）
调用时机 → SKILL.md 4.5
"""

import pandas as pd
import sys
import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from utils import (
    filter_samples, count_multi_select, get_multi_select_cols,
    safe_chi2, fmt_p, get_rank,
)

DATA_PATH = Path(__file__).parent.parent / "references" / "iQOO15U外观测试数据0526.xlsx"

# B6 购后满意度影响因素编码
B6_CODES = {
    1: "喜欢产品设计风格", 2: "喜欢颜色/配色", 3: "喜欢机身形状/大小",
    4: "屏幕/屏幕边框", 5: "摄像头模组设计", 6: "中框/边角",
    7: "后盖材质观感", 8: "机身重量", 9: "握持手感",
    10: "后盖材质触感", 11: "做工与精致度", 12: "划痕/指纹",
    13: "品牌印象", 14: "社交评价/他人看法", 15: "其他（请注明）",
}

# B7 购后细项满意度编码（与 B6 1-14 对应，但不含 15「其他」）
B7_CODES = {
    1: "整体设计风格", 2: "颜色/配色", 3: "机身形状/大小",
    4: "屏幕/屏幕边框", 5: "摄像头模组设计", 6: "中框/边角",
    7: "后盖材质观感", 8: "后盖材质触感", 9: "机身重量",
    10: "握持手感", 11: "做工与精致度", 12: "划痕/指纹",
    13: "品牌印象", 14: "社交评价/他人看法",
}


def calc_b7_satisfaction(df, code: int) -> dict:
    """
    计算单个 B7 细项的满意度指标。

    返回
    ----
    dict 包含 n, avg_score, sat_pct, neu_pct, dis_pct,
              sat_n, neu_n, dis_n（供卡方检验用）
    """
    col = f"B7__{code}"
    vals = pd.to_numeric(df[col], errors="coerce").dropna()
    n = len(vals)

    if n == 0:
        return {"n": 0, "avg": 0.0, "sat_pct": 0.0, "neu_pct": 0.0,
                "dis_pct": 0.0, "sat_n": 0, "neu_n": 0, "dis_n": 0}

    sat_n = (vals == 5).sum()
    neu_n = (vals == 4).sum()
    dis_n = ((vals >= 1) & (vals <= 3)).sum()

    return {
        "n": n,
        "avg": vals.mean(),
        "sat_pct": sat_n / n * 100,
        "neu_pct": neu_n / n * 100,
        "dis_pct": dis_n / n * 100,
        "sat_n": sat_n,
        "neu_n": neu_n,
        "dis_n": dis_n,
    }


def main():
    data = pd.read_excel(DATA_PATH, "data")
    benpin = filter_samples(data, fz1_val=1, fzs9_val=1)
    jingpin = filter_samples(data, fz1_val=2, fzs9_val=4)

    N1, N2 = len(benpin), len(jingpin)
    if N1 == 0 or N2 == 0:
        print("[ERROR] 该组无购后体验样本，无法计算")
        sys.exit(1)

    # ========== 一、基础样本量 ==========
    print("#### 4.5 购后体验-外观维度指标\n")
    print("##### 一、基础样本量")
    print(f"- 本品外观影响因素有效样本量(N1)：{N1}")
    print(f"- 竞品外观影响因素有效样本量(N2)：{N2}")

    # ========== 二、外观影响因素（B6） ==========
    b6_cols = get_multi_select_cols(data, "B6")
    b6_bp = count_multi_select(benpin, b6_cols)
    b6_jp = count_multi_select(jingpin, b6_cols)

    b6_bp_sorted = sorted(b6_bp.items(), key=lambda x: x[1], reverse=True)
    b6_jp_sorted = sorted(b6_jp.items(), key=lambda x: x[1], reverse=True)

    print("\n##### 二、外观影响因素指标")
    print("| 影响因素名称 | 本品占比 | 本品排名 | 竞品占比 | 竞品排名 | P值 | 显著性判定 |")
    print("|-------------|---------|---------|---------|---------|-----|-----------|")

    for code in sorted(B6_CODES.keys()):
        name = B6_CODES[code]
        x1 = b6_bp.get(code, 0)
        x2 = b6_jp.get(code, 0)
        p_i, sig_i, warn_i = safe_chi2(x1, N1 - x1, x2, N2 - x2)
        print(
            f"| {name} | {x1/N1*100:.2f}% | {get_rank(code, b6_bp_sorted)} | "
            f"{x2/N2*100:.2f}% | {get_rank(code, b6_jp_sorted)} | "
            f"{fmt_p(p_i)} | {sig_i}{warn_i} |"
        )

    # ========== 三、外观细项满意度（B7） ==========
    print("\n##### 三、外观细项满意度指标")
    header = (
        "| 细项名称 | 本品均分 | 本品排名 | 本品满意占比 | 本品中立占比 | 本品不满占比 | "
        "竞品均分 | 竞品排名 | 竞品满意占比 | 竞品中立占比 | 竞品不满占比 | "
        "满意占比P值 | 满意占比判定 | 不满占比P值 | 不满占比判定 |"
    )
    sep = (
        "|---------|-------------|---------|-------------|-------------|-------------|"
        "-------------|---------|-------------|-------------|-------------|"
        "-------------|-------------|-------------|-------------|"
    )
    print(header)
    print(sep)

    # 先收集所有得分用于排名
    bp_scores = {}
    jp_scores = {}
    bp_results = {}
    jp_results = {}

    for code in sorted(B7_CODES.keys()):
        bp_results[code] = calc_b7_satisfaction(benpin, code)
        jp_results[code] = calc_b7_satisfaction(jingpin, code)
        bp_scores[code] = bp_results[code]["avg"]
        jp_scores[code] = jp_results[code]["avg"]

    # 排名
    bp_sorted = sorted(bp_scores.items(), key=lambda x: x[1], reverse=True)
    jp_sorted = sorted(jp_scores.items(), key=lambda x: x[1], reverse=True)

    for code in sorted(B7_CODES.keys()):
        name = B7_CODES[code]
        bp_r = bp_results[code]
        jp_r = jp_results[code]

        # 满意占比卡方检验
        p_sat, sig_sat, warn_sat = safe_chi2(
            bp_r["sat_n"], bp_r["n"] - bp_r["sat_n"],
            jp_r["sat_n"], jp_r["n"] - jp_r["sat_n"],
        )
        # 不满占比卡方检验
        p_dis, sig_dis, warn_dis = safe_chi2(
            bp_r["dis_n"], bp_r["n"] - bp_r["dis_n"],
            jp_r["dis_n"], jp_r["n"] - jp_r["dis_n"],
        )

        print(
            f"| {name} | {bp_r['avg']:.2f} | {get_rank(code, bp_sorted)} | "
            f"{bp_r['sat_pct']:.2f}% | {bp_r['neu_pct']:.2f}% | {bp_r['dis_pct']:.2f}% | "
            f"{jp_r['avg']:.2f} | {get_rank(code, jp_sorted)} | "
            f"{jp_r['sat_pct']:.2f}% | {jp_r['neu_pct']:.2f}% | {jp_r['dis_pct']:.2f}% | "
            f"{fmt_p(p_sat)} | {sig_sat}{warn_sat} | {fmt_p(p_dis)} | {sig_dis}{warn_dis} |"
        )

    # 附加：排名汇总
    print("\n##### 三-附录：满意度得分排名")
    print("\n**本品排名（均分从高到低）**：")
    for i, (c, score) in enumerate(bp_sorted):
        print(f"  {i+1}. {B7_CODES[c]}: {score:.2f}")
    print("\n**竞品排名（均分从高到低）**：")
    for i, (c, score) in enumerate(jp_sorted):
        print(f"  {i+1}. {B7_CODES[c]}: {score:.2f}")


if __name__ == "__main__":
    main()
