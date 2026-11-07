"""ZiWei service 单元测试。"""
import pytest

from app.services.ziwei_service import (
    ZiWeiService, _ziwei_position, _ming_gong_index, _layout_14_main_stars,
    _layout_aux_stars,
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


def test_aux_stars_count_and_kind():
    aux = _layout_aux_stars("壬", "午", 7, 8)
    assert len(aux) == 13
    assert sum(1 for v in aux.values() if v["kind"] == "吉星") == 7
    assert sum(1 for v in aux.values() if v["kind"] == "煞星") == 6


def test_aux_stars_kou_jue():
    """壬午年、农历七月、申时 → 逐星核对安星口诀（0=子 … 11=亥）。"""
    aux = _layout_aux_stars("壬", "午", 7, 8)
    assert aux["左辅"]["idx"] == 10   # 辰起正月顺行至七月 → 戌
    assert aux["右弼"]["idx"] == 4    # 戌起正月逆行至七月 → 辰
    assert aux["文昌"]["idx"] == 2    # 戌起子时逆数至申 → 寅
    assert aux["文曲"]["idx"] == 0    # 辰起子时顺数至申 → 子
    assert aux["天魁"]["idx"] == 3    # 壬癸兔蛇藏 → 卯
    assert aux["天钺"]["idx"] == 5    # → 巳
    assert aux["禄存"]["idx"] == 11   # 壬禄在亥
    assert aux["擎羊"]["idx"] == 0    # 禄存顺行一位 → 子
    assert aux["陀罗"]["idx"] == 10   # 禄存逆行一位 → 戌
    assert aux["火星"]["idx"] == 9    # 寅午戌火起丑，顺数至申 → 酉
    assert aux["铃星"]["idx"] == 11   # 寅午戌铃起卯，顺数至申 → 亥
    assert aux["地劫"]["idx"] == 7    # 亥起子时顺数至申 → 未
    assert aux["地空"]["idx"] == 3    # 亥起子时逆数至申 → 卯


def test_aux_stars_exactly_one_per_palace_slot(sample):
    """整盘里每一颗辅煞星都恰好落在唯一一宫，且 total 计数守恒。"""
    total_main = total_lucky = total_sha = 0
    for p in sample["palaces"]:
        for s in p["stars"]:
            if s["kind"] == "主星":
                total_main += 1
            elif s["kind"] == "吉星":
                total_lucky += 1
            elif s["kind"] == "煞星":
                total_sha += 1
    assert total_main == 14
    assert total_lucky == 7
    assert total_sha == 6
    assert len(sample["stars_position"]) == 14
    assert len(sample["aux_stars_position"]) == 13
    assert len(sample["lucky_stars"]) == 7
    assert len(sample["sha_stars"]) == 6
