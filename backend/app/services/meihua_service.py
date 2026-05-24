"""
梅花易数 (Mei Hua Yi Shu) —— 邵雍心易
=====================================
起卦法：
  1. time : 年支数 + 月数 + 日数 → 上卦； + 时支数 → 下卦； 总和÷6 → 动爻
  2. chars: 字数法：第一组字数→上卦；第二组字数→下卦；总和÷6→动爻
  3. number: 二数法：n1→上卦, n2→下卦, (n1+n2)÷6→动爻

输出：本卦、变卦、互卦、体用、五行生克。
"""
from __future__ import annotations

from datetime import datetime
from typing import Any

from lunar_python import Solar

from app.utils.calendar_core import CalendarCore
from app.utils.hexagrams import (
    TRIGRAMS, hexagram_from_yao, hu_gua, bian_gua,
)


BAGUA_ORDER = ["乾", "兑", "离", "震", "巽", "坎", "艮", "坤"]
DI_ZHI = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

# 五行生克
WUXING_SHENG = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
WUXING_KE = {"木": "土", "土": "水", "水": "火", "火": "金", "金": "木"}


def _relation(ti_wx: str, yong_wx: str) -> str:
    """五行体用关系判断（梅花核心）。"""
    if ti_wx == yong_wx:
        return "比和（吉）"
    if WUXING_SHENG[yong_wx] == ti_wx:
        return "用生体（大吉）"
    if WUXING_SHENG[ti_wx] == yong_wx:
        return "体生用（耗，小凶）"
    if WUXING_KE[yong_wx] == ti_wx:
        return "用克体（凶）"
    if WUXING_KE[ti_wx] == yong_wx:
        return "体克用（吉）"
    return "?"


def _assemble(upper_idx: int, lower_idx: int, moving_yao_idx: int,
              method: str, extra: dict) -> dict[str, Any]:
    upper = BAGUA_ORDER[upper_idx]
    lower = BAGUA_ORDER[lower_idx]
    upper_bin = TRIGRAMS[upper]["binary"]
    lower_bin = TRIGRAMS[lower]["binary"]
    yao = [lower_bin[2], lower_bin[1], lower_bin[0],
           upper_bin[2], upper_bin[1], upper_bin[0]]
    ben = hexagram_from_yao(yao)
    hu = hu_gua(ben)
    bian = bian_gua(ben, [moving_yao_idx])

    # 体用判定：动爻所在卦为"用"，另一卦为"体"
    if moving_yao_idx < 3:  # 下卦动 → 下卦为用
        yong, ti = lower, upper
    else:                    # 上卦动 → 上卦为用
        yong, ti = upper, lower
    ti_wx = TRIGRAMS[ti]["wuxing"]
    yong_wx = TRIGRAMS[yong]["wuxing"]

    return {
        "method": method,
        "extra": extra,
        "upper_trigram": upper,
        "lower_trigram": lower,
        "moving_yao_index_bottom_up": moving_yao_idx,
        "ben_gua": ben.to_dict(),
        "hu_gua": hu.to_dict(),
        "bian_gua": bian.to_dict(),
        "ti_yong": {
            "ti": {"gua": ti, "wuxing": ti_wx},
            "yong": {"gua": yong, "wuxing": yong_wx},
            "relation": _relation(ti_wx, yong_wx),
        },
    }


class MeiHuaService:
    @classmethod
    def by_time(
        cls, birth_time: str, longitude: float, latitude: float,
        is_lunar: bool = False, is_leap_month: bool = False, **_,
    ) -> dict[str, Any]:
        """以一个时刻起卦（默认按真太阳时）。"""
        ctx = CalendarCore.resolve(
            birth_time=birth_time,
            longitude=longitude, latitude=latitude,
            is_lunar=is_lunar, is_leap_month=is_leap_month,
        )
        dt = datetime.strptime(
            ctx["true_solar_time"]["true_solar_time"], "%Y-%m-%d %H:%M:%S"
        )
        solar = Solar.fromYmdHms(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
        lunar = solar.getLunar()
        # 年支序号 (子=1..亥=12)
        year_zhi = lunar.getYearZhi()
        year_zhi_num = DI_ZHI.index(year_zhi) + 1
        month_num = abs(lunar.getMonth())
        day_num = lunar.getDay()
        # 时支序号
        hour_zhi_num = ((dt.hour + 1) // 2) % 12 + 1

        s_upper = year_zhi_num + month_num + day_num
        s_lower = s_upper + hour_zhi_num
        upper_idx = (s_upper - 1) % 8
        lower_idx = (s_lower - 1) % 8
        moving_yao_idx = (s_lower - 1) % 6

        return _assemble(
            upper_idx, lower_idx, moving_yao_idx,
            method="time",
            extra={
                "year_zhi": year_zhi, "lunar_month": month_num,
                "lunar_day": day_num, "hour_zhi_num": hour_zhi_num,
                "s_upper": s_upper, "s_lower": s_lower,
            },
        )

    @classmethod
    def by_chars(cls, part1: str, part2: str) -> dict[str, Any]:
        """字数起卦：part1 字符数 → 上卦；part2 字符数 → 下卦。"""
        n1 = len(part1.strip())
        n2 = len(part2.strip())
        if n1 == 0 or n2 == 0:
            raise ValueError("part1 与 part2 都不能为空")
        upper_idx = (n1 - 1) % 8
        lower_idx = (n2 - 1) % 8
        moving_yao_idx = (n1 + n2 - 1) % 6
        return _assemble(
            upper_idx, lower_idx, moving_yao_idx,
            method="chars", extra={"part1_len": n1, "part2_len": n2},
        )

    @classmethod
    def by_numbers(cls, n1: int, n2: int) -> dict[str, Any]:
        """二数起卦。"""
        upper_idx = (n1 - 1) % 8
        lower_idx = (n2 - 1) % 8
        moving_yao_idx = (n1 + n2 - 1) % 6
        return _assemble(
            upper_idx, lower_idx, moving_yao_idx,
            method="numbers", extra={"n1": n1, "n2": n2},
        )
