"""MeiHua 单元测试。"""
from app.services.meihua_service import MeiHuaService


def test_by_chars_basic():
    # part1 长度 1 → 上卦索引 0 → 乾
    # part2 长度 8 → 下卦索引 7 → 坤
    # 动爻 = (1+8-1)%6 = 2
    r = MeiHuaService.by_chars("一", "梅花易数神乎其技")
    assert r["upper_trigram"] == "乾"
    assert r["lower_trigram"] == "坤"
    assert r["moving_yao_index_bottom_up"] == 2


def test_by_numbers_ti_yong():
    # n1=3 → 上卦索引 2 → 离； n2=5 → 下卦索引 4 → 巽
    # 动爻 = (3+5-1)%6 = 1，下卦动 → 下卦巽为用、上卦离为体
    r = MeiHuaService.by_numbers(3, 5)
    assert r["upper_trigram"] == "离"
    assert r["lower_trigram"] == "巽"
    assert r["ti_yong"]["ti"]["gua"] == "离"
    assert r["ti_yong"]["yong"]["gua"] == "巽"
    # 离=火, 巽=木 → 用(木)生体(火) → 大吉
    assert "用生体" in r["ti_yong"]["relation"]


def test_by_time_runs():
    r = MeiHuaService.by_time(
        birth_time="1990-05-15 14:30:00",
        longitude=116.40, latitude=39.90,
    )
    assert "ben_gua" in r and "hu_gua" in r and "bian_gua" in r


def test_jiemeng_service_search():
    from app.services.jiemeng_service import JieMengService
    r = JieMengService.search("蛇")
    assert r["total_matched"] >= 1
    assert any("蛇" in res["keywords"] for res in r["results"])
