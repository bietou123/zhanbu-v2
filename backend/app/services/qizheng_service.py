"""
七政四余 (Qi Zheng Si Yu) —— 古典星命学排盘
==============================================
- 七政：日(太阳) 月(太阴) 金(金星) 木(木星) 水(水星) 火(火星) 土(土星)
- 四余：罗睺(月北交点) 计都(月南交点) 月孛(月远地点) 紫炁(传统取木星交点近似)

历法核心使用 PyEphem（XEphem-based，免编译）。
"""
from __future__ import annotations

import math
from datetime import datetime, timedelta
from typing import Any

import ephem

from app.utils.calendar_core import CalendarCore
from app.services.analysis import qizheng_analysis


ZODIAC_12 = [
    "白羊", "金牛", "双子", "巨蟹", "狮子", "处女",
    "天秤", "天蝎", "射手", "摩羯", "水瓶", "双鱼",
]

# 二十八宿（简化等分版，先到先得；岁差修正后续优化）
XIU_28 = [
    ("角", 7), ("亢", 4), ("氐", 16), ("房", 5), ("心", 6), ("尾", 19), ("箕", 10),
    ("斗", 26), ("牛", 8), ("女", 11), ("虚", 9), ("危", 15), ("室", 17), ("壁", 9),
    ("奎", 16), ("娄", 12), ("胃", 14), ("昴", 11), ("毕", 17), ("觜", 1), ("参", 9),
    ("井", 33), ("鬼", 4), ("柳", 15), ("星", 7), ("张", 17), ("翼", 19), ("轸", 18),
]


def _to_deg(rad: float) -> float:
    return rad * 180.0 / math.pi


def _longitude_to_zodiac(lon: float) -> dict[str, Any]:
    lon = lon % 360.0
    idx = int(lon // 30)
    return {
        "zodiac": ZODIAC_12[idx],
        "degree": round(lon - idx * 30, 4),
        "longitude": round(lon, 4),
    }


def _longitude_to_xiu(lon: float) -> str:
    lon = lon % 360.0
    acc = 0.0
    for name, width in XIU_28:
        if acc <= lon < acc + width:
            return name
        acc += width
    return XIU_28[-1][0]


def _ecl_long_deg(body: ephem.Body) -> float:
    """ephem 天体 → 黄经（度）。"""
    ecl = ephem.Ecliptic(body)
    return _to_deg(float(ecl.lon)) % 360.0


def _planet_pack(body: ephem.Body, name: str) -> dict[str, Any]:
    lon = _ecl_long_deg(body)
    ecl = ephem.Ecliptic(body)
    return {
        "name": name,
        "longitude": round(lon, 4),
        "latitude": round(_to_deg(float(ecl.lat)), 4),
        "ra": str(body.ra),
        "dec": str(body.dec),
        **_longitude_to_zodiac(lon),
        "xiu": _longitude_to_xiu(lon),
    }


def _mean_lunar_node_long(jd: float) -> float:
    """月球升交点平黄经（度）。
    公式：Ω = 125.04452 - 1934.13626 * T  (T = 儒略世纪)
    Meeus《Astronomical Algorithms》Ch.47
    """
    T = (jd - 2451545.0) / 36525.0
    return (125.04452 - 1934.13626 * T) % 360.0


def _mean_lunar_perigee_long(jd: float) -> float:
    """月球近地点平黄经（度）。
    Π = 83.3532465 + 4069.0137287 * T (Meeus)
    月孛 = 远地点 = Π + 180°
    """
    T = (jd - 2451545.0) / 36525.0
    perigee = (83.3532465 + 4069.0137287 * T) % 360.0
    return (perigee + 180.0) % 360.0  # 远地点 = 月孛


def _ephem_date_from_dt_ut(dt_ut: datetime) -> ephem.Date:
    return ephem.Date((
        dt_ut.year, dt_ut.month, dt_ut.day,
        dt_ut.hour, dt_ut.minute, dt_ut.second + dt_ut.microsecond / 1e6,
    ))


def _julian_day_from_ephem(d: ephem.Date) -> float:
    """ephem.Date 起点为 1899-12-31 12:00 UT，对应 JD 2415020.0。"""
    return float(d) + 2415020.0


class QiZhengService:
    @classmethod
    def compute(
        cls,
        birth_time: str,
        longitude: float,
        latitude: float,
        is_lunar: bool = False,
        is_leap_month: bool = False,
        **_,
    ) -> dict[str, Any]:
        ctx = CalendarCore.resolve(
            birth_time=birth_time,
            longitude=longitude, latitude=latitude,
            is_lunar=is_lunar, is_leap_month=is_leap_month,
        )
        dt = datetime.strptime(
            ctx["true_solar_time"]["true_solar_time"], "%Y-%m-%d %H:%M:%S"
        )
        ut = dt - timedelta(hours=CalendarCore.CST_OFFSET_HOURS)
        edate = _ephem_date_from_dt_ut(ut)
        jd = _julian_day_from_ephem(edate)

        # observer for ra/dec context
        obs = ephem.Observer()
        obs.lon = str(longitude)
        obs.lat = str(latitude)
        obs.date = edate
        obs.pressure = 0  # 关闭折射

        # 七政
        seven_zheng = {}
        planets: list[tuple[str, ephem.Body]] = [
            ("太阳", ephem.Sun(obs)),
            ("太阴", ephem.Moon(obs)),
            ("水星", ephem.Mercury(obs)),
            ("金星", ephem.Venus(obs)),
            ("火星", ephem.Mars(obs)),
            ("木星", ephem.Jupiter(obs)),
            ("土星", ephem.Saturn(obs)),
        ]
        for name, body in planets:
            seven_zheng[name] = _planet_pack(body, name)

        # 四余
        rahu_lon = _mean_lunar_node_long(jd)
        ketu_lon = (rahu_lon + 180.0) % 360.0
        yuebo_lon = _mean_lunar_perigee_long(jd)
        # 紫炁：传统取木星交点周期 28 年的特殊点；此处用木星黄经 + 180° 近似
        jupiter_lon = _ecl_long_deg(ephem.Jupiter(obs))
        zique_lon = (jupiter_lon + 180.0) % 360.0

        four_yu = {
            "罗睺": {**_longitude_to_zodiac(rahu_lon),
                    "xiu": _longitude_to_xiu(rahu_lon),
                    "note": "月北交点（Meeus 平交点公式）"},
            "计都": {**_longitude_to_zodiac(ketu_lon),
                    "xiu": _longitude_to_xiu(ketu_lon),
                    "note": "月南交点 (罗睺+180°)"},
            "月孛": {**_longitude_to_zodiac(yuebo_lon),
                    "xiu": _longitude_to_xiu(yuebo_lon),
                    "note": "月远地点 (近地点+180°)"},
            "紫炁": {**_longitude_to_zodiac(zique_lon),
                    "xiu": _longitude_to_xiu(zique_lon),
                    "note": "近似实现：木星+180°（古制取木星交点 28 年周期）"},
        }

        result = {
            "context": ctx,
            "julian_day_ut": jd,
            "seven_zheng": seven_zheng,
            "four_yu": four_yu,
            "note": (
                "行星位置由 PyEphem 计算（VSOP87 + ELP-2000 历表）；"
                "月交点 / 月孛使用 Meeus 平根公式；二十八宿采用简化等分。"
            ),
        }
        result["analysis"] = qizheng_analysis.analyze(result)
        return result
