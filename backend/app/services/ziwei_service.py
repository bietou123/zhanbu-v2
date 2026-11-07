"""
ZiWei Service —— 紫微斗数排盘
=====================================
基础版（业内公认算法，无任何"硬算"历法）：
  1. 历法基础 → CalendarCore + lunar-python（农历日/时干支保证不出错）
  2. 安命宫 / 身宫 —— 寅起正月、子时起，标准口诀
  3. 五行局 —— 六十甲子纳音局表（命宫干支查表）
  4. 起紫微星 —— 公认数学公式（商余法）
  5. 紫微/天府两大系 14 主星
  6. 四化（年干 → 禄、权、科、忌）
  7. 十二宫宫位 + 宫干（五虎遁年起月法）

  8. 辅星（左辅右弼、文昌文曲、天魁天钺、禄存）
  9. 煞星（擎羊陀罗、火星铃星、地空地劫）

辅星/煞星安星口诀均采用主流三合派（中州派一致），见 _layout_aux_stars。
"""
from __future__ import annotations

import math
from datetime import datetime
from typing import Any

from lunar_python import Solar

from app.utils.calendar_core import CalendarCore
from app.services.analysis import ziwei_analysis


DI_ZHI = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
TIAN_GAN = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]

# 十二宫名称（命宫起，逆排为顺时针：命→父母→福德→田宅→官禄→交友→迁移→疾厄→财帛→子女→夫妻→兄弟）
# 紫微斗数十二宫顺序（从命宫逆数）
PALACE_NAMES = [
    "命宫", "兄弟", "夫妻", "子女", "财帛", "疾厄",
    "迁移", "交友", "官禄", "田宅", "福德", "父母",
]

# 时辰对应（子=0 至 亥=11，每两小时一个时辰）
def _hour_to_zhi_idx(hour: int) -> int:
    # 23:00–00:59 → 子(0)，01:00–02:59 → 丑(1) …
    return ((hour + 1) // 2) % 12


# 六十甲子纳音局表：返回 五行局编号 (水2/木3/金4/土5/火6)
# 表中以"甲子乙丑 海中金" → 金四局, 依此类推
NAYIN_TO_JU = {
    # 金四局
    "甲子": 4, "乙丑": 4, "壬寅": 4, "癸卯": 4, "庚辰": 4, "辛巳": 4,
    "甲午": 4, "乙未": 4, "壬申": 4, "癸酉": 4, "庚戌": 4, "辛亥": 4,
    # 火六局
    "丙寅": 6, "丁卯": 6, "甲戌": 6, "乙亥": 6, "戊子": 6, "己丑": 6,
    "丙申": 6, "丁酉": 6, "甲辰": 6, "乙巳": 6, "戊午": 6, "己未": 6,
    # 木三局
    "戊辰": 3, "己巳": 3, "壬午": 3, "癸未": 3, "庚寅": 3, "辛卯": 3,
    "戊戌": 3, "己亥": 3, "壬子": 3, "癸丑": 3, "庚申": 3, "辛酉": 3,
    # 土五局
    "庚午": 5, "辛未": 5, "戊寅": 5, "己卯": 5, "丙戌": 5, "丁亥": 5,
    "庚子": 5, "辛丑": 5, "戊申": 5, "己酉": 5, "丙辰": 5, "丁巳": 5,
    # 水二局
    "丙子": 2, "丁丑": 2, "甲申": 2, "乙酉": 2, "壬辰": 2, "癸巳": 2,
    "丙午": 2, "丁未": 2, "甲寅": 2, "乙卯": 2, "壬戌": 2, "癸亥": 2,
}
JU_NAME = {2: "水二局", 3: "木三局", 4: "金四局", 5: "土五局", 6: "火六局"}


# 年干四化（紫微斗数最常用的"传统派"四化表）
SI_HUA = {
    "甲": {"禄": "廉贞", "权": "破军", "科": "武曲", "忌": "太阳"},
    "乙": {"禄": "天机", "权": "天梁", "科": "紫微", "忌": "太阴"},
    "丙": {"禄": "天同", "权": "天机", "科": "文昌", "忌": "廉贞"},
    "丁": {"禄": "太阴", "权": "天同", "科": "天机", "忌": "巨门"},
    "戊": {"禄": "贪狼", "权": "太阴", "科": "右弼", "忌": "天机"},
    "己": {"禄": "武曲", "权": "贪狼", "科": "天梁", "忌": "文曲"},
    "庚": {"禄": "太阳", "权": "武曲", "科": "太阴", "忌": "天同"},
    "辛": {"禄": "巨门", "权": "太阳", "科": "文曲", "忌": "文昌"},
    "壬": {"禄": "天梁", "权": "紫微", "科": "左辅", "忌": "武曲"},
    "癸": {"禄": "破军", "权": "巨门", "科": "太阴", "忌": "贪狼"},
}

# 五虎遁：年干 → 寅月天干起始
WU_HU_DUN = {
    "甲": "丙", "己": "丙",
    "乙": "戊", "庚": "戊",
    "丙": "庚", "辛": "庚",
    "丁": "壬", "壬": "壬",
    "戊": "甲", "癸": "甲",
}


def _yin_idx() -> int:
    return DI_ZHI.index("寅")


def _ming_gong_index(lunar_month: int, hour_zhi_idx: int) -> int:
    """
    安命宫：寅宫起正月，顺数至生月；从该宫起子时，逆数至生时 = 命宫。
    返回宫位地支 index (0=子 ... 11=亥)。
    """
    # 寅 顺数 (lunar_month - 1) 宫
    month_zhi = (_yin_idx() + (lunar_month - 1)) % 12
    # 再 逆数 hour_zhi_idx 宫
    ming = (month_zhi - hour_zhi_idx) % 12
    return ming


def _shen_gong_index(lunar_month: int, hour_zhi_idx: int) -> int:
    """安身宫：同上，但起子时后顺数至生时。"""
    month_zhi = (_yin_idx() + (lunar_month - 1)) % 12
    return (month_zhi + hour_zhi_idx) % 12


def _ming_gong_ganzhi(year_gan: str, ming_zhi_idx: int) -> str:
    """五虎遁求宫干：寅宫起 五虎遁之月干，顺排十二宫。"""
    start_gan = WU_HU_DUN[year_gan]
    yin = _yin_idx()
    # 命宫相对于寅宫的偏移
    offset = (ming_zhi_idx - yin) % 12
    gan_idx = (TIAN_GAN.index(start_gan) + offset) % 10
    return TIAN_GAN[gan_idx] + DI_ZHI[ming_zhi_idx]


def _ziwei_position(ju: int, lunar_day: int) -> int:
    """
    起紫微星标准公式（商余法）：
      设 D = 生日，J = 五行局
      q = ceil(D / J)
      r = q * J - D
      r 为偶 → 从寅顺行 (q - 1) 宫，再顺行 r 宫
      r 为奇 → 从寅顺行 (q - 1) 宫，再逆行 r 宫
    返回紫微所在地支 index。
    """
    q = math.ceil(lunar_day / ju)
    r = q * ju - lunar_day
    base = (_yin_idx() + (q - 1)) % 12
    if r % 2 == 0:
        return (base + r) % 12
    else:
        return (base - r) % 12


def _layout_14_main_stars(ziwei_idx: int) -> dict[str, int]:
    """根据紫微位置布 14 主星。"""
    # 紫微星系（逆排）：紫微 / 天机(-1) / 太阳(-3) / 武曲(-4) / 天同(-5) / 廉贞(-8)
    z = ziwei_idx
    tianfu = (4 - z) % 12  # 紫微+天府 ≡ 4 (mod 12)
    stars = {
        "紫微": z,
        "天机": (z - 1) % 12,
        "太阳": (z - 3) % 12,
        "武曲": (z - 4) % 12,
        "天同": (z - 5) % 12,
        "廉贞": (z - 8) % 12,
        "天府": tianfu,
        "太阴": (tianfu + 1) % 12,
        "贪狼": (tianfu + 2) % 12,
        "巨门": (tianfu + 3) % 12,
        "天相": (tianfu + 4) % 12,
        "天梁": (tianfu + 5) % 12,
        "七杀": (tianfu + 6) % 12,
        "破军": (tianfu + 10) % 12,
    }
    return stars


# ───────────────── 辅星 / 煞星 ─────────────────

# 天魁天钺（年干）：口诀「甲戊庚牛羊，乙己鼠猴乡，丙丁猪鸡位，壬癸兔蛇藏，六辛逢马虎」
KUI_YUE = {
    "甲": (1, 7), "戊": (1, 7), "庚": (1, 7),   # 丑未
    "乙": (0, 8), "己": (0, 8),                  # 子申
    "丙": (11, 9), "丁": (11, 9),                # 亥酉
    "辛": (6, 2),                                # 午寅
    "壬": (3, 5), "癸": (3, 5),                  # 卯巳
}

# 禄存（年干）：甲寅 乙卯 丙戊巳 丁己午 庚申 辛酉 壬亥 癸子
LU_CUN = {
    "甲": 2, "乙": 3, "丙": 5, "丁": 6, "戊": 5,
    "己": 6, "庚": 8, "辛": 9, "壬": 11, "癸": 0,
}

# 火星铃星起点（年支三合）：(火星宫, 铃星宫)
HUO_LING_START = {
    "寅": (1, 3), "午": (1, 3), "戌": (1, 3),   # 火丑 铃卯
    "申": (2, 10), "子": (2, 10), "辰": (2, 10),  # 火寅 铃戌
    "巳": (3, 10), "酉": (3, 10), "丑": (3, 10),  # 火卯 铃戌
    "亥": (9, 10), "卯": (9, 10), "未": (9, 10),  # 火酉 铃戌
}

AUX_LUCKY = ["左辅", "右弼", "文昌", "文曲", "天魁", "天钺", "禄存"]
AUX_SHA = ["擎羊", "陀罗", "火星", "铃星", "地空", "地劫"]


def _layout_aux_stars(
    year_gan: str, year_zhi: str, lunar_month: int, hour_zhi_idx: int
) -> dict[str, dict]:
    """
    安辅星与煞星。返回 {星名: {"idx": 地支index, "kind": "吉星"/"煞星"}}。

    口诀（三合派）：
      左辅：辰宫起正月顺行至生月       右弼：戌宫起正月逆行至生月
      文昌：戌宫起子时逆数至生时       文曲：辰宫起子时顺数至生时
      天魁天钺：年干查表
      禄存：年干查表；擎羊 = 禄存顺行一位，陀罗 = 禄存逆行一位
      火星铃星：年支三合定起点，顺数至生时
      地劫：亥宫起子时顺行至生时       地空：亥宫起子时逆行至生时
    """
    month_step = (lunar_month - 1) % 12
    out: dict[str, dict] = {}

    out["左辅"] = {"idx": (4 + month_step) % 12, "kind": "吉星"}   # 辰=4
    out["右弼"] = {"idx": (10 - month_step) % 12, "kind": "吉星"}  # 戌=10
    out["文昌"] = {"idx": (10 - hour_zhi_idx) % 12, "kind": "吉星"}
    out["文曲"] = {"idx": (4 + hour_zhi_idx) % 12, "kind": "吉星"}

    kui, yue = KUI_YUE[year_gan]
    out["天魁"] = {"idx": kui, "kind": "吉星"}
    out["天钺"] = {"idx": yue, "kind": "吉星"}

    lu = LU_CUN[year_gan]
    out["禄存"] = {"idx": lu, "kind": "吉星"}
    out["擎羊"] = {"idx": (lu + 1) % 12, "kind": "煞星"}
    out["陀罗"] = {"idx": (lu - 1) % 12, "kind": "煞星"}

    huo_start, ling_start = HUO_LING_START[year_zhi]
    out["火星"] = {"idx": (huo_start + hour_zhi_idx) % 12, "kind": "煞星"}
    out["铃星"] = {"idx": (ling_start + hour_zhi_idx) % 12, "kind": "煞星"}

    out["地劫"] = {"idx": (11 + hour_zhi_idx) % 12, "kind": "煞星"}  # 亥=11 顺行
    out["地空"] = {"idx": (11 - hour_zhi_idx) % 12, "kind": "煞星"}

    return out


class ZiWeiService:
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

        # 紫微以"农历月日"和"真太阳时辰"为输入
        solar = Solar.fromYmdHms(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
        lunar = solar.getLunar()
        lunar_month = abs(lunar.getMonth())  # 闰月也按其月数算（流派不一，此处用主流）
        lunar_day = lunar.getDay()
        hour_zhi_idx = _hour_to_zhi_idx(dt.hour)
        year_ganzhi = lunar.getYearInGanZhi()
        year_gan = year_ganzhi[0]
        year_zhi = year_ganzhi[1]

        # 1. 命宫 / 身宫
        ming = _ming_gong_index(lunar_month, hour_zhi_idx)
        shen = _shen_gong_index(lunar_month, hour_zhi_idx)

        # 2. 命宫干支 + 五行局
        ming_ganzhi = _ming_gong_ganzhi(year_gan, ming)
        ju = NAYIN_TO_JU[ming_ganzhi]

        # 3. 起紫微
        ziwei_idx = _ziwei_position(ju, lunar_day)
        stars = _layout_14_main_stars(ziwei_idx)
        aux = _layout_aux_stars(year_gan, year_zhi, lunar_month, hour_zhi_idx)

        # 4. 安四化
        si_hua = SI_HUA[year_gan]

        # 5. 十二宫（从命宫逆数：命→兄弟→夫妻→…→父母）
        palaces = []
        for i, name in enumerate(PALACE_NAMES):
            zhi_idx = (ming - i) % 12
            offset = (zhi_idx - _yin_idx()) % 12
            gan_idx = (TIAN_GAN.index(WU_HU_DUN[year_gan]) + offset) % 10
            palace_ganzhi = TIAN_GAN[gan_idx] + DI_ZHI[zhi_idx]

            # 主星在前，辅星次之，煞星最后
            here = [({"name": s, "kind": "主星"}, s) for s, idx in stars.items() if idx == zhi_idx]
            here += [({"name": s, "kind": info["kind"]}, s) for s, info in aux.items() if info["idx"] == zhi_idx]

            palace_stars_with_hua = []
            for star, s in here:
                hua = next((k for k, v in si_hua.items() if v == s), None)
                if hua:
                    star["si_hua"] = hua
                palace_stars_with_hua.append(star)

            palaces.append({
                "name": name,
                "zhi": DI_ZHI[zhi_idx],
                "ganzhi": palace_ganzhi,
                "is_shen_gong": (zhi_idx == shen),
                "stars": palace_stars_with_hua,
            })

        result = {
            "context": ctx,
            "lunar": {
                "year_ganzhi": year_ganzhi,
                "lunar_month": lunar_month,
                "lunar_day": lunar_day,
                "hour_zhi": DI_ZHI[hour_zhi_idx],
                "is_leap_month": lunar.getMonth() < 0,
            },
            "ming_gong": {
                "zhi": DI_ZHI[ming],
                "ganzhi": ming_ganzhi,
            },
            "shen_gong": {"zhi": DI_ZHI[shen]},
            "wu_xing_ju": {"code": ju, "name": JU_NAME[ju]},
            "ziwei_position": DI_ZHI[ziwei_idx],
            "stars_position": {k: DI_ZHI[v] for k, v in stars.items()},
            "aux_stars_position": {
                k: {"zhi": DI_ZHI[v["idx"]], "kind": v["kind"]} for k, v in aux.items()
            },
            "lucky_stars": AUX_LUCKY,
            "sha_stars": AUX_SHA,
            "si_hua": si_hua,
            "palaces": palaces,
            "note": "14 主星 + 7 吉星 + 6 煞星 + 四化 + 十二宫。",
        }
        result["analysis"] = ziwei_analysis.analyze(result)
        return result
