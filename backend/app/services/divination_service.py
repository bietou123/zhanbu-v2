"""
占卜起卦 (Divination) —— 六爻金钱卦
======================================
支持两种起卦法：
  1. coin: 摇钱起卦法 (3 枚铜钱投 6 次)
     - 三背=老阳(动)  三面=老阴(动)
     - 二背一面=少阴  二面一背=少阳
  2. numbers: 三数报数起卦法（梅花式但用 6 爻爻变规则）
     - 第一数 ÷ 8 取余 → 上卦
     - 第二数 ÷ 8 取余 → 下卦
     - 三数和 ÷ 6 取余 → 动爻位置

输出本卦、变卦、互卦、错卦、综卦及爻辞。
"""
from __future__ import annotations

import random
from typing import Any

from app.utils.hexagrams import (
    Hexagram, hexagram_from_yao, TRIGRAMS, BIN_TO_TRIGRAM,
    hu_gua, cuo_gua, zong_gua, bian_gua,
)
from app.services.analysis import divination_analysis


# 八卦序（先天/后天混用，此处用文王后天：乾兑离震巽坎艮坤）
BAGUA_ORDER = ["乾", "兑", "离", "震", "巽", "坎", "艮", "坤"]


def _flip_coins() -> tuple[int, bool]:
    """
    投 3 枚铜钱。背为阳，面为阴。
    返回 (爻值 0/1, 是否动爻)
    """
    coins = [random.randint(0, 1) for _ in range(3)]  # 1=背阳, 0=面阴
    bei_count = sum(coins)
    # 三背→老阳(动阳=1) 三面→老阴(动阴=0)
    # 二背一面→少阴(静阴=0) 一背二面→少阳(静阳=1)
    if bei_count == 3:
        return 1, True
    elif bei_count == 0:
        return 0, True
    elif bei_count == 2:
        return 1, False  # 少阳
    else:
        return 0, False  # 少阴


def _gua_by_coin(seed: int | None = None) -> tuple[list[int], list[int]]:
    """投 6 次得六爻（自下而上），返回 (爻值, 动爻索引列表)。"""
    if seed is not None:
        random.seed(seed)
    yao, moving = [], []
    for i in range(6):
        v, d = _flip_coins()
        yao.append(v)
        if d:
            moving.append(i)
    return yao, moving


def _gua_by_numbers(n1: int, n2: int, n3: int) -> tuple[list[int], list[int]]:
    """三数报数起卦：n1→上卦, n2→下卦, n3→动爻。"""
    upper_idx = (n1 - 1) % 8
    lower_idx = (n2 - 1) % 8
    moving_yao = (n3 - 1) % 6  # 0~5
    upper_bin = TRIGRAMS[BAGUA_ORDER[upper_idx]]["binary"]
    lower_bin = TRIGRAMS[BAGUA_ORDER[lower_idx]]["binary"]
    # yao 自下而上：lower (下,中,上) + upper (下,中,上)
    yao = [lower_bin[2], lower_bin[1], lower_bin[0],
           upper_bin[2], upper_bin[1], upper_bin[0]]
    return yao, [moving_yao]


class DivinationService:
    @classmethod
    def by_coin(cls, seed: int | None = None) -> dict[str, Any]:
        yao, moving = _gua_by_coin(seed)
        return cls._assemble(yao, moving, method="coin")

    @classmethod
    def by_numbers(cls, n1: int, n2: int, n3: int) -> dict[str, Any]:
        yao, moving = _gua_by_numbers(n1, n2, n3)
        return cls._assemble(
            yao, moving, method="numbers",
            extra={"n1": n1, "n2": n2, "n3": n3},
        )

    @classmethod
    def _assemble(cls, yao: list[int], moving: list[int],
                  method: str, extra: dict | None = None) -> dict[str, Any]:
        ben = hexagram_from_yao(yao)
        hu = hu_gua(ben)
        cuo = cuo_gua(ben)
        zong = zong_gua(ben)
        bian = bian_gua(ben, moving) if moving else ben

        result = {
            "method": method,
            "extra": extra or {},
            "moving_yao_indexes_bottom_up": moving,
            "ben_gua": ben.to_dict(),
            "bian_gua": bian.to_dict(),
            "hu_gua": hu.to_dict(),
            "cuo_gua": cuo.to_dict(),
            "zong_gua": zong.to_dict(),
        }
        result["analysis"] = divination_analysis.analyze(result)
        return result
