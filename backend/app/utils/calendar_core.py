"""
CalendarCore —— 詹卜历法核心
==========================================
排盘 0 容错。所有公农历转换、干支、节气、真太阳时均委派给成熟库：

- `lunar-python`  : 公农历互转、四柱八字、节气、干支
- 均时差: Spencer 1971 公式（精度 ~30 秒，对八字/紫微/奇门起盘绰绰有余）

本模块只做"封装与编排"，**绝不自己推演历法/天文公式**——除均时差用学界公认闭式公式外。
"""
from __future__ import annotations

import math
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from typing import Any

from lunar_python import Solar, Lunar


@dataclass
class TrueSolarTimeResult:
    civil_time: str
    longitude: float
    longitude_offset_min: float
    eot_min: float
    true_solar_time: str
    delta_total_min: float


@dataclass
class GanZhiResult:
    year: str
    month: str
    day: str
    hour: str
    zodiac: str
    na_yin: dict[str, str]


class CalendarCore:
    CST_OFFSET_HOURS: float = 8.0
    CST_STANDARD_LONGITUDE: float = 120.0

    # ---------- 公农历 ----------
    @classmethod
    def solar_to_lunar(cls, dt: datetime) -> dict[str, Any]:
        solar = Solar.fromYmdHms(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
        lunar = solar.getLunar()
        return {
            "lunar_year": lunar.getYear(),
            "lunar_month": lunar.getMonth(),
            "lunar_day": lunar.getDay(),
            "is_leap_month": lunar.getMonth() < 0,
            "year_in_ganzhi": lunar.getYearInGanZhi(),
            "month_in_ganzhi": lunar.getMonthInGanZhi(),
            "day_in_ganzhi": lunar.getDayInGanZhi(),
            "time_in_ganzhi": lunar.getTimeInGanZhi(),
            "zodiac": lunar.getYearShengXiao(),
            "jieqi": lunar.getJieQi(),
        }

    @classmethod
    def lunar_to_solar(
        cls, year: int, month: int, day: int,
        hour: int = 0, minute: int = 0, second: int = 0,
        is_leap_month: bool = False,
    ) -> datetime:
        m = -abs(month) if is_leap_month else abs(month)
        lunar = Lunar.fromYmdHms(year, m, day, hour, minute, second)
        solar = lunar.getSolar()
        return datetime(solar.getYear(), solar.getMonth(), solar.getDay(),
                        solar.getHour(), solar.getMinute(), solar.getSecond())

    # ---------- 真太阳时 ----------
    @classmethod
    def true_solar_time(cls, dt: datetime, longitude: float) -> TrueSolarTimeResult:
        """
        真太阳时 = 北京时间 + (longitude - 120°) * 4 min  + EoT(分钟)
        """
        longitude_offset_min = (longitude - cls.CST_STANDARD_LONGITUDE) * 4.0
        eot_min = cls._equation_of_time_minutes(dt)
        delta_total_min = longitude_offset_min + eot_min
        true_dt = dt + timedelta(minutes=delta_total_min)
        return TrueSolarTimeResult(
            civil_time=dt.strftime("%Y-%m-%d %H:%M:%S"),
            longitude=longitude,
            longitude_offset_min=round(longitude_offset_min, 4),
            eot_min=round(eot_min, 4),
            true_solar_time=true_dt.strftime("%Y-%m-%d %H:%M:%S"),
            delta_total_min=round(delta_total_min, 4),
        )

    @staticmethod
    def _equation_of_time_minutes(dt: datetime) -> float:
        """
        Spencer 1971 闭式均时差公式。
        参考：Spencer, J. W. "Fourier series representation of the position of the sun."
        Search 2.5 (1971): 172.
        精度 ~30 秒，行业气象/航天/八字均认可。
        """
        # 用 UT
        ut = dt - timedelta(hours=CalendarCore.CST_OFFSET_HOURS)
        # 当年累计日
        start_of_year = datetime(ut.year, 1, 1)
        n = (ut - start_of_year).days + 1 + (ut.hour + ut.minute / 60.0) / 24.0
        B = 2 * math.pi * (n - 1) / 365.0
        eot = 229.18 * (
            0.000075
            + 0.001868 * math.cos(B)
            - 0.032077 * math.sin(B)
            - 0.014615 * math.cos(2 * B)
            - 0.04089 * math.sin(2 * B)
        )
        return eot

    # ---------- 四柱 ----------
    @classmethod
    def ganzhi_from_true_solar(cls, true_dt: datetime) -> GanZhiResult:
        solar = Solar.fromYmdHms(true_dt.year, true_dt.month, true_dt.day,
                                 true_dt.hour, true_dt.minute, true_dt.second)
        lunar = solar.getLunar()
        ec = lunar.getEightChar()
        return GanZhiResult(
            year=ec.getYear(), month=ec.getMonth(),
            day=ec.getDay(), hour=ec.getTime(),
            zodiac=lunar.getYearShengXiao(),
            na_yin={"year": ec.getYearNaYin(), "month": ec.getMonthNaYin(),
                    "day": ec.getDayNaYin(), "hour": ec.getTimeNaYin()},
        )

    # ---------- 一站式 ----------
    @classmethod
    def resolve(
        cls, birth_time: str, longitude: float, latitude: float,
        is_lunar: bool = False, is_leap_month: bool = False,
    ) -> dict[str, Any]:
        dt = datetime.strptime(birth_time, "%Y-%m-%d %H:%M:%S")
        if is_lunar:
            dt = cls.lunar_to_solar(
                dt.year, dt.month, dt.day,
                dt.hour, dt.minute, dt.second,
                is_leap_month=is_leap_month,
            )
        tst = cls.true_solar_time(dt, longitude)
        true_dt = datetime.strptime(tst.true_solar_time, "%Y-%m-%d %H:%M:%S")
        return {
            "input": {
                "birth_time": birth_time, "is_lunar": is_lunar,
                "is_leap_month": is_leap_month,
                "longitude": longitude, "latitude": latitude,
            },
            "solar_civil": dt.strftime("%Y-%m-%d %H:%M:%S"),
            "true_solar_time": asdict(tst),
            "lunar": cls.solar_to_lunar(true_dt),
            "ganzhi": asdict(cls.ganzhi_from_true_solar(true_dt)),
        }
