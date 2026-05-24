"""XiaoLiuRen 单元测试。"""
from app.services.xiaoliuren_service import XiaoLiuRenService, _step, GUA


def test_step_zheng_yue_chu_yi_zi_shi():
    # 正月初一子时 → 应当全在大安
    m, d, t = _step(1, 1, 0)
    assert m == "大安" and d == "大安" and t == "大安"


def test_step_eryue_chusan_wushi():
    # 二月初三午时（午=6）
    m, d, t = _step(2, 3, 6)
    assert m == GUA[(2 - 1) % 6]   # 留连
    assert d == GUA[(1 + 2) % 6]    # 赤口
    # 时位 = (赤口 idx + 6) % 6 = 3 → 赤口
    assert t == GUA[(3 + 6) % 6]


def test_compute_sample():
    r = XiaoLiuRenService.compute(
        birth_time="1990-05-15 14:30:00",
        longitude=116.40, latitude=39.90,
        is_lunar=False,
    )
    assert r["primary"] in GUA
    assert "san_chuan" in r
    assert set(r["san_chuan"].keys()) == {"月将", "日将", "时将"}
