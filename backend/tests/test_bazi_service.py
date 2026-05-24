"""BaZi service 单元测试。"""
import pytest
from app.services.bazi_service import BaZiService, _ten_god


@pytest.fixture
def sample():
    return BaZiService.compute(
        birth_time="1990-05-15 14:30:00",
        gender=1,
        longitude=116.40, latitude=39.90,
    )


def test_pillars(sample):
    assert sample["pillars"]["year"] == "庚午"
    # 日主庚金
    assert sample["day_master"]["gan"] == "庚" or sample["day_master"]["wuxing"] == "金"


def test_ten_god_self_is_self():
    assert _ten_god("甲", "甲") == "比肩"
    assert _ten_god("甲", "乙") == "劫财"
    assert _ten_god("甲", "丙") == "食神"
    assert _ten_god("甲", "丁") == "伤官"
    assert _ten_god("甲", "戊") == "偏财"
    assert _ten_god("甲", "己") == "正财"
    assert _ten_god("甲", "庚") == "七杀"
    assert _ten_god("甲", "辛") == "正官"
    assert _ten_god("甲", "壬") == "偏印"
    assert _ten_god("甲", "癸") == "正印"


def test_wuxing_count_sum(sample):
    s = sum(sample["wuxing_count"].values())
    # 天干 4 + 地支藏干总和（地支共 4 个，藏干 1-3 个）
    assert 4 + 4 <= s <= 4 + 12


def test_da_yun_10_steps(sample):
    assert len(sample["da_yun"]) == 10
    for d in sample["da_yun"]:
        assert len(d["ganzhi"]) == 2


def test_liu_nian_next_10(sample):
    assert len(sample["liu_nian_next_10y"]) == 10
