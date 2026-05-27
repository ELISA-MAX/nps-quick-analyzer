"""
第四步 - 4.3：购前吸引-外观维度指标计算
==================================
数据来源：
  - B1（Q1 购前吸引大项，多选）：当时吸引您最终购买[FZ1]的主要原因
  - B2（Q2 购前吸引细项，多选）：以下哪些外观设计有吸引到您

输出：
  1. 基础样本量 N1/N2, M1/M2
  2. 外观大项占比、排名、本品 vs 竞品卡方检验
  3. 外观细项占比、排名、本品 vs 竞品卡方检验
调用时机 → SKILL.md 4.3
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

# --- B1 购前吸引大项编码含义 ---
B1_CODES = {
    1: "外观/手感/材质/工艺", 2: "续航/电池", 3: "品牌", 4: "前置摄像头镜头/自拍",
    5: "后置摄像头镜头/拍照", 6: "音质/音效/声音", 7: "游戏体验", 8: "价格/性价比",
    9: "售后服务/权益", 10: "尝新尝鲜", 11: "大屏期待", 12: "存储容量",
    13: "芯片/CPU（速度）", 14: "AI功能", 15: "支持5G", 16: "电池容量/续航时间",
    17: "无线充电功率/速度", 18: "屏幕显示效果", 19: "操作系统", 20: "通讯/信号",
    21: "散热效果", 22: "防水防尘", 23: "防摔", 24: "指纹解锁", 25: "面部解锁",
    26: "品牌/IP联名款", 27: "其他", 90: "其他（请注明）",
}

# --- B2 购前吸引细项编码含义 ---
B2_CODES = {
    1: "整体设计风格", 2: "前置摄像头形状/位置", 3: "后置摄像头模组Deco设计",
    4: "后置摄像头凸起高度", 5: "后置摄像头的大小尺寸", 6: "后置摄像头的灯效",
    7: "后盖材质观感（亮度、透明度等）", 8: "后盖材质触感（光滑度、细腻度等）",
    9: "边框/中框设计（与屏幕的衔接、天线槽样式等）", 10: "边框/中框材质感（亮度、质感等）",
    11: "配色", 12: "厚度", 13: "重量", 14: "屏幕尺寸/机身尺寸",
    15: "屏占比", 16: "屏幕边框宽度", 17: "屏幕形态（曲面/直屏等）",
    18: "屏幕R角", 19: "其他（请注明）", 20: "没有特别吸引我的地方",
}


def main():
    data = pd.read_excel(DATA_PATH, "data")
    benpin = filter_samples(data, fz1_val=1, fzs9_val=1)
    jingpin = filter_samples(data, fz1_val=2, fzs9_val=4)

    N1, N2 = len(benpin), len(jingpin)
    if N1 == 0 or N2 == 0:
        print("[ERROR] 该组无购前吸引样本，无法计算大项指标")
        sys.exit(1)

    # --- B1 大项统计 ---
    b1_cols = get_multi_select_cols(data, "B1")
    b1_bp = count_multi_select(benpin, b1_cols)
    b1_jp = count_multi_select(jingpin, b1_cols)

    M1 = b1_bp.get(1, 0)  # 本品外观大项样本量
    M2 = b1_jp.get(1, 0)  # 竞品外观大项样本量

    # --- B2 细项统计 ---
    b2_cols = get_multi_select_cols(data, "B2")
    b2_bp = count_multi_select(benpin, b2_cols)
    b2_jp = count_multi_select(jingpin, b2_cols)

    # ========== 输出 ==========
    print("#### 4.3 购前吸引-外观维度指标\n")

    # 一、基础样本量
    print("##### 一、基础样本量")
    print(f"- 本品购前吸引总样本量(N1)：{N1}")
    print(f"- 竞品购前吸引总样本量(N2)：{N2}")
    print(f"- 本品外观吸引样本量(M1)：{M1}")
    print(f"- 竞品外观吸引样本量(M2)：{M2}")

    # 二、外观大项指标
    b1_bp_sorted = sorted(b1_bp.items(), key=lambda x: x[1], reverse=True)
    b1_jp_sorted = sorted(b1_jp.items(), key=lambda x: x[1], reverse=True)

    p, sig, warn = safe_chi2(M1, N1 - M1, M2, N2 - M2)

    print("\n##### 二、外观大项指标")
    print("| 分组 | 外观大项占比 | 排名 | P值 | 显著性判定 |")
    print("|------|-------------|------|-----|-----------|")
    print(f"| 本品 | {M1/N1*100:.2f}% | {get_rank(1, b1_bp_sorted)} | - | - |")
    print(f"| 竞品 | {M2/N2*100:.2f}% | {get_rank(1, b1_jp_sorted)} | - | - |")
    print(f"| 本品vs竞品 | - | - | {fmt_p(p)} | {sig}{warn} |")

    # 三、外观细项指标
    print("\n##### 三、外观细项指标")
    if M1 == 0 or M2 == 0:
        print("[WARN] 该组无外观吸引样本，无法计算细项指标")
        return

    b2_bp_sorted = sorted(b2_bp.items(), key=lambda x: x[1], reverse=True)
    b2_jp_sorted = sorted(b2_jp.items(), key=lambda x: x[1], reverse=True)

    print(f"| 细项名称 | 本品占比 | 本品排名 | 竞品占比 | 竞品排名 | P值 | 显著性判定 |")
    print(f"|---------|---------|---------|---------|---------|-----|-----------|")

    for code in sorted(B2_CODES.keys()):
        name = B2_CODES[code]
        x1 = b2_bp.get(code, 0)
        x2 = b2_jp.get(code, 0)
        pct1 = x1 / M1 * 100 if M1 > 0 else 0
        pct2 = x2 / M2 * 100 if M2 > 0 else 0

        p_i, sig_i, warn_i = safe_chi2(x1, M1 - x1, x2, M2 - x2)
        print(
            f"| {name} | {pct1:.2f}% | {get_rank(code, b2_bp_sorted)} | "
            f"{pct2:.2f}% | {get_rank(code, b2_jp_sorted)} | "
            f"{fmt_p(p_i)} | {sig_i}{warn_i} |"
        )


if __name__ == "__main__":
    main()
