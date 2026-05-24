"""QiMen service 单元测试。"""
import pytest
from app.services.qimen_service import QiMenService, _layout_di_pan


def test_di_pan_yang_dun_1_ju():
    """阳遁1局：戊落 1 宫，其余顺布。"""
    di_pan = _layout_di_pan(1, is_yang=True)
    assert di_pan[1] == "戊"
    assert di_pan[2] == "己"
    assert di_pan[9] == "乙"


def test_di_pan_yin_dun_9_ju():
    """阴遁9局：戊落 9 宫，其余逆布。"""
    di_pan = _layout_di_pan(9, is_yang=False)
    assert di_pan[9] == "戊"
    assert di_pan[8] == "己"


def test_di_pan_complete_9_palaces():
    di_pan = _layout_di_pan(5, is_yang=True)
    assert len(di_pan) == 9
    assert set(di_pan.values()) == {"戊", "己", "庚", "辛", "壬", "癸", "丁", "丙", "乙"}


@pytest.fixture
def sample():
    return QiMenService.compute(
        birth_time="1990-05-15 14:30:00",
        longitude=116.40, latitude=39.90,
    )


def test_compute_basic_fields(sample):
    assert sample["dun"] in {"阳遁", "阴遁"}
    assert 1 <= sample["ju"] <= 9
    assert sample["yuan"] in {"上元", "中元", "下元"}
    assert len(sample["palaces"]) == 9


def test_each_palace_has_star_and_gate_or_center(sample):
    for p in sample["palaces"]:
        assert p["star"]
        # 中宫 5 没有门
        if p["palace"] == 5:
            assert p["gate"] is None
        else:
            assert p["gate"]
