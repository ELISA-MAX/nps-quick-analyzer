"""
通用工具模块 —— 所有步骤共用的辅助函数与全局常量。
被 step1~step4_5 各脚本 import 使用，无需独立运行。
"""

import numpy as np
from scipy.stats import chi2_contingency


def safe_chi2(a: int, b: int, c: int, d: int):
    """
    安全的 Pearson 卡方独立性检验（2×2 列联表）。

    参数
    ----
    a, b : 第一行（本品/竞品或分组1）的 [选中数, 未选中数]
    c, d : 第二行（另一分组）的 [选中数, 未选中数]

    返回
    ----
    p : float 或 nan  P 值
    sig : str         "差异显著" / "差异不显著" / "无法计算"
    warn : str         "" 或 理论频数/零频警告文本
    """
    table = [[a, b], [c, d]]
    try:
        chi2, p, dof, expected = chi2_contingency(table)
        sig = "差异显著" if p < 0.05 else "差异不显著"
        warn = ""
        if expected.min() < 5:
            warn = "（理论频数不足，结果仅供参考）"
        return p, sig, warn
    except ValueError:
        return float("nan"), "无法计算", "（理论频数含零，无法进行卡方检验）"


def fmt_p(p: float) -> str:
    """将 P 值格式化为 4 位小数（若 < 0.0001 则显示 P<0.0001）。"""
    if np.isnan(p):
        return "-"
    if p < 0.0001:
        return "P<0.0001"
    return f"{p:.4f}"


def get_rank(code: int, sorted_list: list) -> str:
    """
    在按 count 降序排列的 (code, count) 列表中查找指定 code 的排名。
    返回格式："第X名/共Y项"
    """
    total = len(sorted_list)
    for i, (c, _) in enumerate(sorted_list):
        if c == code:
            return f"第{i+1}名/共{total}项"
    return "-"


def filter_samples(data, fz1_val, fzs9_val):
    """
    按 FZ1 和 FZS9 筛选样本。

    本品：FZ1=1 & FZS9=1 (iQOO 15 Ultra 用户，对比了 iPhone)
    竞品：FZ1=2 & FZS9=4 (iPhone 17 Pro Max 用户，对比了 iQOO)
    """
    return data[(data["FZ1"] == fz1_val) & (data["FZS9"] == fzs9_val)]


def count_multi_select(data, columns):
    """
    统计多选题各选项的选择人数。

    参数
    ----
    data : DataFrame  已筛选的样本
    columns : list    多选题列名列表（不含 __open 结尾列）

    返回
    ----
    dict : {code_int: count}
    """
    result = {}
    for col in columns:
        code = int(col.split("__")[1])
        result[code] = (data[col] == 1).sum()
    return result


def get_multi_select_cols(data, prefix):
    """
    获取指定前缀的多选题列名（排除 __open 开放题列）。

    示例
    ----
    get_multi_select_cols(data, "B1") → ["B1__1", "B1__2", ..., "B1__90"]
    """
    return [c for c in data.columns if c.startswith(prefix + "__") and not c.endswith("__open")]
