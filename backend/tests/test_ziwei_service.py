"""ZiWei service 单元测试。"""
import pytest

from app.services.ziwei_service import (
    ZiWeiService, _ziwei_position, _ming_gong_index, _layout_14_main_stars,
)


def test_ziwei_position_formula():
    # 水二局，初一 → 紫微在丑
    assert _ziwei_position(2, 1) == 1     # 丑
    # 水二局，初二 → 紫微在寅
    assert _ziwei_position(2, 2) == 2     # 寅
    # 水二局，初三 → 紫微在寅 (验证奇数余数逆飞)
    assert _ziwei_position(2, 3) == 2
    # 水二局，初四 → 紫微在卯
    assert _ziwei_position(2, 4) == 3


def test_ming_gong_yin_zheng_yue_zi_shi():
    # 正月生 + 子时 → 命宫在寅
    assert _ming_gong_index(1, 0) == 2   # 寅


def test_14_stars_complete():
    stars = _layout_14_main_stars(0)
    assert len(stars) == 14
    # 紫微+天府之和（按 mod 12 计算）应当为 4
    assert (stars["紫微"] + stars["天府"]) % 12 == 4


@pytest.fixture
def sample():
    return ZiWeiService.compute(
        birth_time="1990-05-15 14:30:00",
        gender=1,
        longitude=116.40, latitude=39.90,
    )


def test_palaces_12(sample):
    assert len(sample["palaces"]) == 12
    names = [p["name"] for p in sample["palaces"]]
    assert names[0] == "命宫"
    assert "夫妻" in names
    assert "官禄" in names


def test_wuxing_ju_in_range(sample):
    assert sample["wu_xing_ju"]["code"] in {2, 3, 4, 5, 6}


def test_si_hua_for_year_gan(sample):
    si_hua = sample["si_hua"]
    assert set(si_hua.keys()) == {"禄", "权", "科", "忌"}
