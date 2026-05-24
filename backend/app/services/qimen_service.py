"""
QiMen DunJia Service —— 时家奇门遁甲排盘
================================================
基础版（时家转盘标准算法）：
  1. 历法 → CalendarCore + lunar-python（节气、四柱）
  2. 阴阳遁判断（冬至→夏至 阳遁，夏至→冬至 阴遁）
  3. 定局（节气 + 三元 → 1~9 局）
  4. 布地盘三奇六仪
  5. 排九星、八门、八神
  6. 标注值符、值使

进阶（超神接气、置闰、活盘）后续 milestone 增补。
"""
from __future__ import annotations

from datetime import datetime
from typing import Any

from lunar_python import Solar

from app.utils.calendar_core import CalendarCore


# 洛书九宫：宫位 → 后天八卦方位
# 1=坎(北)  2=坤(西南) 3=震(东)  4=巽(东南)
# 5=中宫    6=乾(西北) 7=兑(西)  8=艮(东北) 9=离(南)
PALACE_BAGUA = {
    1: ("坎", "北"), 2: ("坤", "西南"), 3: ("震", "东"), 4: ("巽", "东南"),
    5: ("中", "中"), 6: ("乾", "西北"), 7: ("兑", "西"), 8: ("艮", "东北"), 9: ("离", "南"),
}

# 九星（按宫位 1-9）
NINE_STARS = ["天蓬", "天芮", "天冲", "天辅", "天禽", "天心", "天柱", "天任", "天英"]

# 八门（按宫位 1-9，中宫无门，5=中寄 2）
EIGHT_GATES_MAP = {
    1: "休门", 2: "死门", 3: "伤门", 4: "杜门",
    5: None,  # 中宫无门
    6: "开门", 7: "惊门", 8: "生门", 9: "景门",
}

# 八神（值符/腾蛇/太阴/六合/白虎/玄武/九地/九天）
EIGHT_SPIRITS = ["值符", "腾蛇", "太阴", "六合", "白虎", "玄武", "九地", "九天"]

# 节气 → 局数（上元/中元/下元）
# 阳遁九节气（冬至→芒种）+ 阴遁九节气（夏至→大雪）
# 标准三元局表
JIE_QI_JU = {
    # 阳遁
    "冬至": (1, 7, 4), "小寒": (2, 8, 5), "大寒": (3, 9, 6),
    "立春": (8, 5, 2), "雨水": (9, 6, 3), "惊蛰": (1, 7, 4),
    "春分": (3, 9, 6), "清明": (4, 1, 7), "谷雨": (5, 2, 8),
    "立夏": (4, 1, 7), "小满": (5, 2, 8), "芒种": (6, 3, 9),
    # 阴遁
    "夏至": (9, 3, 6), "小暑": (8, 2, 5), "大暑": (7, 1, 4),
    "立秋": (2, 5, 8), "处暑": (1, 4, 7), "白露": (9, 3, 6),
    "秋分": (7, 1, 4), "寒露": (6, 9, 3), "霜降": (5, 8, 2),
    "立冬": (6, 9, 3), "小雪": (5, 8, 2), "大雪": (4, 7, 1),
}

YANG_DUN_JIEQI = {
    "冬至", "小寒", "大寒", "立春", "雨水", "惊蛰",
    "春分", "清明", "谷雨", "立夏", "小满", "芒种",
}

# 60甲子分上中下三元（每5天一元，按日干支起符头：甲己日为符头）
# 上元: 甲子→戊辰；中元: 己巳→癸酉；下元: 甲戌→戊寅 … 循环
JIA_ZI_60 = [
    "甲子", "乙丑", "丙寅", "丁卯", "戊辰", "己巳", "庚午", "辛未", "壬申", "癸酉",
    "甲戌", "乙亥", "丙子", "丁丑", "戊寅", "己卯", "庚辰", "辛巳", "壬午", "癸未",
    "甲申", "乙酉", "丙戌", "丁亥", "戊子", "己丑", "庚寅", "辛卯", "壬辰", "癸巳",
    "甲午", "乙未", "丙申", "丁酉", "戊戌", "己亥", "庚子", "辛丑", "壬寅", "癸卯",
    "甲辰", "乙巳", "丙午", "丁未", "戊申", "己酉", "庚戌", "辛亥", "壬子", "癸丑",
    "甲寅", "乙卯", "丙辰", "丁巳", "戊午", "己未", "庚申", "辛酉", "壬戌", "癸亥",
]

# 三奇六仪标准排序：戊己庚辛壬癸（六仪）+ 丁丙乙（三奇）
LIU_YI_SAN_QI = ["戊", "己", "庚", "辛", "壬", "癸", "丁", "丙", "乙"]

# 阳遁九局：第 N 局表示"戊"落在第 N 宫；阴遁九局：戊落第 N 宫但逆飞
# 阳遁布局顺序：宫位 1→2→3→4→5→6→7→8→9（顺飞）
# 阴遁布局顺序：宫位 9→8→7→6→5→4→3→2→1（逆飞）


def _yuan_index(day_ganzhi: str) -> int:
    """根据日干支判断上(0)/中(1)/下(2)元。
    符头（甲子/己卯/甲戌等"甲己日"）开始 5 天为一元。
    简化：取日干支在 60 甲子中的位置 // 5 % 3 = 元数。
    """
    idx = JIA_ZI_60.index(day_ganzhi)
    return (idx // 5) % 3


def _layout_di_pan(ju: int, is_yang: bool) -> dict[int, str]:
    """
    布地盘三奇六仪。
    返回 {宫位: 字}，五行局编号 ju ∈ 1..9。
    阳遁：戊起 ju 宫，顺布（戊→己→庚→辛→壬→癸→丁→丙→乙，按宫位序）
    阴遁：戊起 ju 宫，逆布
    """
    di_pan: dict[int, str] = {}
    # 宫位顺序（阳遁顺、阴遁逆）：1,2,3,4,5,6,7,8,9 (顺) ；9,8,7,6,5,4,3,2,1 (逆)
    order = list(range(1, 10)) if is_yang else list(range(9, 0, -1))
    start_pos = order.index(ju)
    for i, label in enumerate(LIU_YI_SAN_QI):
        palace = order[(start_pos + i) % 9]
        di_pan[palace] = label
    return di_pan


def _zhi_fu_zhi_shi(
    hour_ganzhi: str, di_pan: dict[int, str]
) -> dict[str, Any]:
    """
    定值符值使：时干在天盘对应宫 = 值符宫；时支对应宫 = 值使宫。
    简化版：以时干所在地盘宫为值符；时支对应固定宫（子=1, 丑=8, ... 标准对应）。
    """
    hour_gan = hour_ganzhi[0]
    hour_zhi = hour_ganzhi[1]
    # 找时干在地盘哪个宫
    zhi_fu_palace = next((p for p, g in di_pan.items() if g == hour_gan), None)
    # 时支落宫表（标准奇门时支宫位）
    ZHI_TO_PALACE = {
        "子": 1, "丑": 8, "寅": 8, "卯": 3, "辰": 4, "巳": 4,
        "午": 9, "未": 2, "申": 2, "酉": 7, "戌": 6, "亥": 6,
    }
    zhi_shi_palace = ZHI_TO_PALACE[hour_zhi]
    return {
        "zhi_fu_palace": zhi_fu_palace,
        "zhi_fu_star": NINE_STARS[zhi_fu_palace - 1] if zhi_fu_palace else None,
        "zhi_shi_palace": zhi_shi_palace,
        "zhi_shi_gate": EIGHT_GATES_MAP[zhi_shi_palace],
    }


class QiMenService:
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
        tst = ctx["true_solar_time"]["true_solar_time"]
        dt = datetime.strptime(tst, "%Y-%m-%d %H:%M:%S")

        solar = Solar.fromYmdHms(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
        lunar = solar.getLunar()
        ec = lunar.getEightChar()

        # 1. 节气（取当前所在节气，使用 lunar-python 的 prev jieqi）
        jq_table = lunar.getJieQiTable()
        # 找当前时间之前最近的节气
        current_jieqi, current_jieqi_date = None, None
        for name, jq_solar in jq_table.items():
            jq_dt = datetime(
                jq_solar.getYear(), jq_solar.getMonth(), jq_solar.getDay(),
                jq_solar.getHour(), jq_solar.getMinute(),
            )
            if jq_dt <= dt and name in JIE_QI_JU:
                if current_jieqi_date is None or jq_dt > current_jieqi_date:
                    current_jieqi = name
                    current_jieqi_date = jq_dt
        if current_jieqi is None:
            current_jieqi = "冬至"  # 兜底

        # 2. 阴阳遁
        is_yang = current_jieqi in YANG_DUN_JIEQI

        # 3. 定局（节气 + 三元）
        day_ganzhi = ec.getDay()
        yuan = _yuan_index(day_ganzhi)  # 0 上 / 1 中 / 2 下
        ju = JIE_QI_JU[current_jieqi][yuan]

        # 4. 布地盘三奇六仪
        di_pan = _layout_di_pan(ju, is_yang)

        # 5. 值符值使
        hour_ganzhi = ec.getTime()
        zfzs = _zhi_fu_zhi_shi(hour_ganzhi, di_pan)

        # 6. 整理九宫输出
        palaces_out = []
        for p in range(1, 10):
            bagua, fang = PALACE_BAGUA[p]
            palaces_out.append({
                "palace": p,
                "bagua": bagua,
                "direction": fang,
                "di_pan": di_pan[p],
                "star": NINE_STARS[p - 1],
                "gate": EIGHT_GATES_MAP[p],
            })

        return {
            "context": ctx,
            "jieqi": current_jieqi,
            "jieqi_time": current_jieqi_date.strftime("%Y-%m-%d %H:%M:%S")
                if current_jieqi_date else None,
            "dun": "阳遁" if is_yang else "阴遁",
            "yuan": ["上元", "中元", "下元"][yuan],
            "ju": ju,
            "ju_label": f"{'阳' if is_yang else '阴'}遁{ju}局",
            "day_ganzhi": day_ganzhi,
            "hour_ganzhi": hour_ganzhi,
            "zhi_fu_zhi_shi": zfzs,
            "palaces": palaces_out,
            "spirits_order": EIGHT_SPIRITS,
            "note": "基础版：地盘+九星+八门+值符值使；天盘飞布、超神接气后续增补。",
        }
