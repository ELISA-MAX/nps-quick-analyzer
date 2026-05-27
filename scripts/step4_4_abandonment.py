"""
第四步 - 4.4：购前放弃购买-外观维度指标计算
======================================
数据来源：
  - D1_1（弃购本品 iQOO 大项，多选）：对比过 iQOO 但最终没买的原因
  - D1_3（弃购竞品 iPhone 大项，多选）：对比过 iPhone 但最终没买的原因
  - D2_1（弃购本品外观细项，多选）：对 iQOO 外观哪些方面最不满意
  - D2_3（弃购竞品外观细项，多选）：对 iPhone 外观哪些方面最不满意

样本对应关系（重要）：
  本品弃购样本 (N1) = 竞品购买者 (FZ1=2 & FZS9=4) → 他们为啥没买 iQOO
  竞品弃购样本 (N2) = 本品购买者 (FZ1=1 & FZS9=1) → 他们为啥没买 iPhone
调用时机 → SKILL.md 4.4
"""

import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from utils import (
    filter_samples, count_multi_select, get_multi_select_cols,
    safe_chi2, fmt_p, get_rank,
)

DATA_PATH = Path(__file__).parent.parent / "references" / "iQOO15U外观测试数据0526.xlsx"

# D1 弃购大项编码
D1_CODES = {
    1: "外观/手感/材质/工艺不好", 2: "硬件配置不行", 3: "价格/性价比不行",
    4: "做工不行", 5: "续航/电池不行", 6: "产品品质/品控不行", 7: "品牌不行",
    8: "身边人不用", 9: "售后服务/权益少", 10: "操作系统体验不好",
    11: "功能不行", 90: "其他（请注明）",
}

# D2 弃购细项编码
D2_CODES = {
    1: "整体设计风格", 2: "配色/颜色", 3: "机身形状/大小", 4: "屏幕/屏幕边框",
    5: "摄像头模组设计", 6: "中框/边角", 7: "后盖材质观感", 8: "机身重量",
    9: "握持手感", 10: "后盖材质触感", 11: "做工与精致度", 12: "划痕/指纹",
    13: "品牌印象", 14: "社交评价/他人看法", 15: "其他（请注明）",
}


def main():
    data = pd.read_excel(DATA_PATH, "data")

    # --- 样本定义 ---
    # 本品弃购样本：iPhone 购买者 (FZ1=2) 对比过 iQOO (FZS9=4)，回答 D1_1 / D2_1
    jingpin = filter_samples(data, fz1_val=2, fzs9_val=4)
    # 竞品弃购样本：iQOO 购买者 (FZ1=1) 对比过 iPhone (FZS9=1)，回答 D1_3 / D2_3
    benpin = filter_samples(data, fz1_val=1, fzs9_val=1)

    N1, N2 = len(jingpin), len(benpin)  # N1=本品弃购, N2=竞品弃购

    if N1 == 0 or N2 == 0:
        print("[ERROR] 该组无弃购样本，无法计算大项指标")
        sys.exit(1)

    # --- D1 大项统计 ---
    d1_1_cols = get_multi_select_cols(data, "D1_1")
    d1_3_cols = get_multi_select_cols(data, "D1_3")

    d1_1_counts = count_multi_select(jingpin, d1_1_cols)  # 弃购本品
    d1_3_counts = count_multi_select(benpin, d1_3_cols)   # 弃购竞品

    M1 = d1_1_counts.get(1, 0)  # 本品外观弃购
    M2 = d1_3_counts.get(1, 0)  # 竞品外观弃购

    # --- D2 细项统计 ---
    d2_1_cols = get_multi_select_cols(data, "D2_1")
    d2_3_cols = get_multi_select_cols(data, "D2_3")

    d2_1_counts = count_multi_select(jingpin, d2_1_cols)
    d2_3_counts = count_multi_select(benpin, d2_3_cols)

    # ========== 输出 ==========
    print("#### 4.4 购前放弃购买-外观维度指标\n")

    # 一、基础样本量
    print("##### 一、基础样本量")
    print(f"- 本品弃购总样本量(N1)：{N1}")
    print(f"- 竞品弃购总样本量(N2)：{N2}")
    print(f"- 本品外观弃购样本量(M1)：{M1}")
    print(f"- 竞品外观弃购样本量(M2)：{M2}")

    # 二、外观大项指标
    d1_1_sorted = sorted(d1_1_counts.items(), key=lambda x: x[1], reverse=True)
    d1_3_sorted = sorted(d1_3_counts.items(), key=lambda x: x[1], reverse=True)

    p, sig, warn = safe_chi2(M1, N1 - M1, M2, N2 - M2)

    print("\n##### 二、外观大项指标")
    print("| 分组 | 外观大项占比 | 排名 | P值 | 显著性判定 |")
    print("|------|-------------|------|-----|-----------|")
    print(f"| 本品 | {M1/N1*100:.2f}% | {get_rank(1, d1_1_sorted)} | - | - |")
    print(f"| 竞品 | {M2/N2*100:.2f}% | {get_rank(1, d1_3_sorted)} | - | - |")
    print(f"| 本品vs竞品 | - | - | {fmt_p(p)} | {sig}{warn} |")

    # 三、外观细项指标
    print("\n##### 三、外观细项指标")
    if M1 == 0 or M2 == 0:
        print("[WARN] 该组无外观弃购样本，无法计算细项指标")
        return

    d2_1_sorted = sorted(d2_1_counts.items(), key=lambda x: x[1], reverse=True)
    d2_3_sorted = sorted(d2_3_counts.items(), key=lambda x: x[1], reverse=True)

    print(f"| 细项名称 | 本品占比 | 本品排名 | 竞品占比 | 竞品排名 | P值 | 显著性判定 |")
    print(f"|---------|---------|---------|---------|---------|-----|-----------|")

    for code in sorted(D2_CODES.keys()):
        name = D2_CODES[code]
        x1 = d2_1_counts.get(code, 0)
        x2 = d2_3_counts.get(code, 0)
        pct1 = x1 / M1 * 100 if M1 > 0 else 0
        pct2 = x2 / M2 * 100 if M2 > 0 else 0

        p_i, sig_i, warn_i = safe_chi2(x1, M1 - x1, x2, M2 - x2)
        print(
            f"| {name} | {pct1:.2f}% | {get_rank(code, d2_1_sorted)} | "
            f"{pct2:.2f}% | {get_rank(code, d2_3_sorted)} | "
            f"{fmt_p(p_i)} | {sig_i}{warn_i} |"
        )


if __name__ == "__main__":
    main()
