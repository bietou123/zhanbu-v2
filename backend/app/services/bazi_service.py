"""
BaZi Service —— 八字排盘
================================
基于 lunar-python EightChar，做以下封装：
  1. 四柱 + 纳音 + 旬空
  2. 十神（以日主为基准）
  3. 五行强弱统计
  4. 大运（起运 + 10 步）
  5. 流年（默认未来 10 年）
  6. 神煞（lunar-python 自带）

所有"历法计算"都委派给 lunar-python，本模块只做"含义层映射"。
"""
from __future__ import annotations

from datetime import datetime
from typing import Any

from lunar_python import Solar

from app.utils.calendar_core import CalendarCore


TIAN_GAN = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
DI_ZHI = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

GAN_YIN_YANG = {g: ("阳" if i % 2 == 0 else "阴") for i, g in enumerate(TIAN_GAN)}

GAN_WUXING = {
    "甲": "木", "乙": "木",
    "丙": "火", "丁": "火",
    "戊": "土", "己": "土",
    "庚": "金", "辛": "金",
    "壬": "水", "癸": "水",
}
ZHI_WUXING = {
    "寅": "木", "卯": "木",
    "巳": "火", "午": "火",
    "辰": "土", "戌": "土", "丑": "土", "未": "土",
    "申": "金", "酉": "金",
    "亥": "水", "子": "水",
}
ZHI_CANG_GAN = {
    "子": ["癸"],
    "丑": ["己", "癸", "辛"],
    "寅": ["甲", "丙", "戊"],
    "卯": ["乙"],
    "辰": ["戊", "乙", "癸"],
    "巳": ["丙", "庚", "戊"],
    "午": ["丁", "己"],
    "未": ["己", "丁", "乙"],
    "申": ["庚", "壬", "戊"],
    "酉": ["辛"],
    "戌": ["戊", "辛", "丁"],
    "亥": ["壬", "甲"],
}

WUXING_SHENG = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
WUXING_KE = {"木": "土", "土": "水", "水": "火", "火": "金", "金": "木"}


def _ten_god(day_gan: str, other_gan: str) -> str:
    if day_gan == other_gan:
        return "比肩"
    dw, ow = GAN_WUXING[day_gan], GAN_WUXING[other_gan]
    dy, oy = GAN_YIN_YANG[day_gan], GAN_YIN_YANG[other_gan]
    same_yy = dy == oy
    if dw == ow:
        return "比肩" if same_yy else "劫财"
    if WUXING_SHENG[dw] == ow:
        return "食神" if same_yy else "伤官"
    if WUXING_KE[dw] == ow:
        return "偏财" if same_yy else "正财"
    if WUXING_KE[ow] == dw:
        return "七杀" if same_yy else "正官"
    if WUXING_SHENG[ow] == dw:
        return "偏印" if same_yy else "正印"
    return "?"


class BaZiService:
    @classmethod
    def compute(
        cls,
        birth_time: str,
        gender: int,
        longitude: float,
        latitude: float,
        is_lunar: bool = False,
        is_leap_month: bool = False,
    ) -> dict[str, Any]:
        ctx = CalendarCore.resolve(
            birth_time=birth_time,
            longitude=longitude, latitude=latitude,
            is_lunar=is_lunar, is_leap_month=is_leap_month,
        )

        tst = ctx["true_solar_time"]["true_solar_time"]
        dt = datetime.strptime(tst, "%Y-%m-%d %H:%M:%S")
        solar = Solar.fromYmdHms(
            dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second
        )
        lunar = solar.getLunar()
        ec = lunar.getEightChar()
        ec.setSect(2)  # 晚子时算次日（业内通用）
        yun = ec.getYun(gender)

        pillars = {
            "year": ec.getYear(),
            "month": ec.getMonth(),
            "day": ec.getDay(),
            "hour": ec.getTime(),
        }
        day_gan = pillars["day"][0]

        ten_gods_gan = {
            k: ("日主" if k == "day" else _ten_god(day_gan, v[0]))
            for k, v in pillars.items()
        }
        ten_gods_zhi_canggan = {
            k: [
                {"gan": cg, "ten_god": _ten_god(day_gan, cg)}
                for cg in ZHI_CANG_GAN[v[1]]
            ]
            for k, v in pillars.items()
        }

        wuxing_count = {"金": 0, "木": 0, "水": 0, "火": 0, "土": 0}
        for v in pillars.values():
            wuxing_count[GAN_WUXING[v[0]]] += 1
            for cg in ZHI_CANG_GAN[v[1]]:
                wuxing_count[GAN_WUXING[cg]] += 1

        da_yun_list = []
        # 索引 0 是"起运前"，干支为空，跳过；多取 1 个保证 10 步真实大运
        for d in yun.getDaYun(11):
            if not d.getGanZhi():
                continue
            da_yun_list.append({
                "index": d.getIndex(),
                "start_year": d.getStartYear(),
                "start_age": d.getStartAge(),
                "end_year": d.getEndYear(),
                "end_age": d.getEndAge(),
                "ganzhi": d.getGanZhi(),
            })
            if len(da_yun_list) >= 10:
                break

        current_year = datetime.now().year
        liu_nian_list = []
        for offset in range(10):
            y = current_year + offset
            ly_solar = Solar.fromYmd(y, 6, 1)
            ly_lunar = ly_solar.getLunar()
            liu_nian_list.append({
                "year": y,
                "ganzhi": ly_lunar.getYearInGanZhi(),
                "zodiac": ly_lunar.getYearShengXiao(),
            })

        shensha = {
            "day_position_xi": lunar.getDayPositionXi(),
            "day_position_yang_gui": lunar.getDayPositionYangGui(),
            "day_position_yin_gui": lunar.getDayPositionYinGui(),
            "day_position_fu": lunar.getDayPositionFu(),
            "day_position_cai": lunar.getDayPositionCai(),
            "year_nine_star": lunar.getYearNineStar().getNameInXuanKong(),
            "month_nine_star": lunar.getMonthNineStar().getNameInXuanKong(),
            "day_nine_star": lunar.getDayNineStar().getNameInXuanKong(),
            "time_nine_star": lunar.getTimeNineStar().getNameInXuanKong(),
        }

        xun_kong = {
            "year": ec.getYearXunKong(),
            "month": ec.getMonthXunKong(),
            "day": ec.getDayXunKong(),
            "hour": ec.getTimeXunKong(),
        }

        return {
            "context": ctx,
            "pillars": pillars,
            "day_master": {
                "gan": day_gan,
                "wuxing": GAN_WUXING[day_gan],
                "yin_yang": GAN_YIN_YANG[day_gan],
            },
            "ten_gods": {
                "gan": ten_gods_gan,
                "zhi_canggan": ten_gods_zhi_canggan,
            },
            "wuxing_count": wuxing_count,
            "na_yin": {
                "year": ec.getYearNaYin(),
                "month": ec.getMonthNaYin(),
                "day": ec.getDayNaYin(),
                "hour": ec.getTimeNaYin(),
            },
            "xun_kong": xun_kong,
            "qi_yun": {
                "start_solar": yun.getStartSolar().toYmdHms(),
                "start_year": yun.getStartYear(),
                "start_month": yun.getStartMonth(),
                "start_day": yun.getStartDay(),
            },
            "da_yun": da_yun_list,
            "liu_nian_next_10y": liu_nian_list,
            "shensha": shensha,
        }
