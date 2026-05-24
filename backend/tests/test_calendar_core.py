"""
CalendarCore 单元测试 —— 用于自证"不犯错"。
运行:  cd backend && pytest -v
"""
from datetime import datetime
import pytest

from app.utils.calendar_core import CalendarCore


# ---------- 真太阳时 ----------
def test_true_solar_time_beijing_noon():
    """北京经度 116.40 在春分附近，钟表中午 12:00 的真太阳时应略早于 12:00"""
    dt = datetime(2024, 3, 21, 12, 0, 0)
    res = CalendarCore.true_solar_time(dt, longitude=116.40)
    # 经度时差: (116.40 - 120) * 4 = -14.4 分钟
    assert res.longitude_offset_min == pytest.approx(-14.4, abs=0.01)
    # 均时差在春分前后约 -7 ~ +8 分钟，量级合理
    assert -20.0 < res.eot_min < 20.0
    # 总修正应等于两者之和
    assert res.delta_total_min == pytest.approx(
        res.longitude_offset_min + res.eot_min, abs=1e-6
    )


def test_true_solar_time_at_standard_longitude():
    """正好在东经 120° 上，经度时差应为 0"""
    dt = datetime(2024, 6, 21, 12, 0, 0)
    res = CalendarCore.true_solar_time(dt, longitude=120.0)
    assert res.longitude_offset_min == pytest.approx(0.0, abs=1e-6)


# ---------- 公农历 ----------
def test_solar_to_lunar_known_date():
    """2000-01-01 公历 → 农历 1999-11-25"""
    dt = datetime(2000, 1, 1, 12, 0, 0)
    lunar = CalendarCore.solar_to_lunar(dt)
    assert lunar["lunar_year"] == 1999
    assert lunar["lunar_month"] == 11
    assert lunar["lunar_day"] == 25


def test_lunar_to_solar_roundtrip():
    """农历 → 公历 → 农历 应当回到原值"""
    original = datetime(2023, 5, 1, 10, 0, 0)  # 当作农历
    solar = CalendarCore.lunar_to_solar(2023, 5, 1, 10, 0, 0, is_leap_month=False)
    lunar = CalendarCore.solar_to_lunar(solar)
    assert lunar["lunar_year"] == 2023
    assert abs(lunar["lunar_month"]) == 5
    assert lunar["lunar_day"] == 1


# ---------- 干支 ----------
def test_ganzhi_known_birth():
    """1990-05-15 14:30 北京 一组已知干支，用真太阳时排"""
    dt = datetime(1990, 5, 15, 14, 30, 0)
    tst = CalendarCore.true_solar_time(dt, longitude=116.40)
    true_dt = datetime.strptime(tst.true_solar_time, "%Y-%m-%d %H:%M:%S")
    gz = CalendarCore.ganzhi_from_true_solar(true_dt)
    # 1990 年农历庚午年
    assert gz.year == "庚午"
    assert gz.zodiac == "马"
    # 四柱应当各自为两字
    for col in (gz.year, gz.month, gz.day, gz.hour):
        assert len(col) == 2


# ---------- 一站式 ----------
def test_resolve_full_pipeline():
    data = CalendarCore.resolve(
        birth_time="1990-05-15 14:30:00",
        longitude=116.40, latitude=39.90,
        is_lunar=False, is_leap_month=False,
    )
    assert "true_solar_time" in data
    assert "lunar" in data
    assert "ganzhi" in data
    assert data["ganzhi"]["year"] == "庚午"
