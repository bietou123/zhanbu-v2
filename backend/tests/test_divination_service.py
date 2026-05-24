"""Divination 单元测试。"""
from app.services.divination_service import DivinationService
from app.utils.hexagrams import (
    hexagram_from_yao, hu_gua, cuo_gua, zong_gua, bian_gua,
)


def test_coin_seeded_reproducible():
    r1 = DivinationService.by_coin(seed=42)
    r2 = DivinationService.by_coin(seed=42)
    assert r1["ben_gua"]["name"] == r2["ben_gua"]["name"]
    assert r1["moving_yao_indexes_bottom_up"] == r2["moving_yao_indexes_bottom_up"]


def test_numbers_method():
    r = DivinationService.by_numbers(1, 8, 6)
    # n1=1 上卦=乾, n2=8 下卦=坤, n3=6 动爻=5(上爻)
    assert r["ben_gua"]["upper"] == "乾"
    assert r["ben_gua"]["lower"] == "坤"
    # 乾上坤下 = 天地否
    assert r["ben_gua"]["name"] == "天地否"


def test_hexagram_transforms():
    # 乾为天，全阳爻
    h = hexagram_from_yao([1, 1, 1, 1, 1, 1])
    assert h.info()["name"] == "乾为天"
    # 错卦 = 坤为地
    assert cuo_gua(h).info()["name"] == "坤为地"
    # 综卦 = 自身（乾为天的综卦还是乾）
    assert zong_gua(h).info()["name"] == "乾为天"
    # 互卦 = 乾为天（连续阳爻的互卦仍是乾）
    assert hu_gua(h).info()["name"] == "乾为天"
    # 变卦：初九动 → 天风姤
    assert bian_gua(h, [0]).info()["name"] == "天风姤"
