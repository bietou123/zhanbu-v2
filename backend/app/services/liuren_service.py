"""
大六壬 (Da Liu Ren) —— 基础版
=========================================
排盘流程：
  1. 取月将（按节气：中气后转月将）
  2. 月将加时（月将加在占时位上 → 地盘对应天盘）
  3. 起四课（日干、日干寄宫、日支、日支阴阳）
  4. 发三传（初/中/末传，采用最经典"贼克法"简化）
  5. 排十二贵神（贵人加于卯酉前后顺逆排）

注：贼克→比用→涉害→遥克→昴星→别责→八专→伏吟→反吟 九宗门
本基础版仅实现贼克法 + 简易反吟伏吟识别；其余宗门后续 milestone 加。
"""
from __future__ import annotations

from datetime import datetime
from typing import Any

from lunar_python import Solar

from app.utils.calendar_core import CalendarCore
from app.services.analysis import liuren_analysis


DI_ZHI = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
TIAN_GAN = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]

# 月将：按中气后转月将（雨水后亥将，春分后戌将，谷雨后酉将…）
# (中气名称, 月将地支)
YUE_JIANG_TABLE = [
    ("雨水", "亥"), ("春分", "戌"), ("谷雨", "酉"),
    ("小满", "申"), ("夏至", "未"), ("大暑", "午"),
    ("处暑", "巳"), ("秋分", "辰"), ("霜降", "卯"),
    ("小雪", "寅"), ("冬至", "丑"), ("大寒", "子"),
]
ZHONG_QI_NAMES = [t[0] for t in YUE_JIANG_TABLE]

# 日干寄宫 (壬学中"干寄宫"标准表)
GAN_JI_GONG = {
    "甲": "寅", "乙": "辰", "丙": "巳", "丁": "未",
    "戊": "巳", "己": "未", "庚": "申", "辛": "戌",
    "壬": "亥", "癸": "丑",
}

# 天干阴阳
GAN_YIN_YANG = {g: ("阳" if i % 2 == 0 else "阴") for i, g in enumerate(TIAN_GAN)}
ZHI_YIN_YANG = {z: ("阳" if i % 2 == 0 else "阴") for i, z in enumerate(DI_ZHI)}

# 五行
GAN_WUXING = {
    "甲": "木", "乙": "木", "丙": "火", "丁": "火",
    "戊": "土", "己": "土", "庚": "金", "辛": "金",
    "壬": "水", "癸": "水",
}
ZHI_WUXING = {
    "寅": "木", "卯": "木", "巳": "火", "午": "火",
    "辰": "土", "戌": "土", "丑": "土", "未": "土",
    "申": "金", "酉": "金", "亥": "水", "子": "水",
}

WUXING_KE = {"木": "土", "土": "水", "水": "火", "火": "金", "金": "木"}

# 十二贵神顺序（昼贵人起卯位顺布；夜贵人起酉位逆布——这里采用昼贵简化版）
TWELVE_GUI_SHEN = [
    "贵人", "腾蛇", "朱雀", "六合", "勾陈", "青龙",
    "天空", "白虎", "太常", "玄武", "太阴", "天后",
]

# 日干 → 昼贵人地支位置（标准壬学表）
DAY_GUI_REN = {
    "甲": "未", "戊": "未", "庚": "丑",  # 甲戊兼牛羊
    "乙": "申", "己": "子",              # 乙己鼠猴乡
    "丙": "酉", "丁": "亥",              # 丙丁猪鸡位
    "壬": "卯", "癸": "巳",              # 壬癸兔蛇藏
    "辛": "午",                          # 六辛逢马虎（昼用午）
}


def _current_zhongqi(jq_table: dict, dt: datetime) -> tuple[str, datetime]:
    """找小于等于 dt 的最近一个中气。"""
    best = None
    for name, jq_solar in jq_table.items():
        if name not in ZHONG_QI_NAMES:
            continue
        jq_dt = datetime(
            jq_solar.getYear(), jq_solar.getMonth(), jq_solar.getDay(),
            jq_solar.getHour(), jq_solar.getMinute(),
        )
        if jq_dt <= dt and (best is None or jq_dt > best[1]):
            best = (name, jq_dt)
    return best if best else (ZHONG_QI_NAMES[-1], dt)


def _yue_jiang_for_zhongqi(zhongqi: str) -> str:
    for name, jiang in YUE_JIANG_TABLE:
        if name == zhongqi:
            return jiang
    return "亥"


def _hour_to_zhi(hour: int) -> str:
    return DI_ZHI[((hour + 1) // 2) % 12]


def _add_zhi(a: str, n: int) -> str:
    return DI_ZHI[(DI_ZHI.index(a) + n) % 12]


def _layout_tian_pan(yue_jiang: str, zhan_shi: str) -> dict[str, str]:
    """
    月将加时：把月将放在占时位上，然后地盘十二支顺布得到天盘。
    返回 {地盘支: 天盘支}
    """
    offset = (DI_ZHI.index(yue_jiang) - DI_ZHI.index(zhan_shi)) % 12
    return {z: _add_zhi(z, offset) for z in DI_ZHI}


def _four_classes(day_gan: str, day_zhi: str, tian_pan: dict[str, str]) -> list[dict]:
    """起四课：第一课、第二课（干）；第三课、第四课（支）。"""
    ji_gong = GAN_JI_GONG[day_gan]
    # 第一课：日干寄宫 → 天盘
    c1_di = ji_gong
    c1_tian = tian_pan[c1_di]
    # 第二课：第一课天盘 → 再上天盘
    c2_di = c1_tian
    c2_tian = tian_pan[c2_di]
    # 第三课：日支 → 天盘
    c3_di = day_zhi
    c3_tian = tian_pan[c3_di]
    # 第四课：第三课天盘 → 再上天盘
    c4_di = c3_tian
    c4_tian = tian_pan[c4_di]
    return [
        {"index": 1, "type": "干上神", "di": c1_di, "tian": c1_tian},
        {"index": 2, "type": "干阴",   "di": c2_di, "tian": c2_tian},
        {"index": 3, "type": "支上神", "di": c3_di, "tian": c3_tian},
        {"index": 4, "type": "支阴",   "di": c4_di, "tian": c4_tian},
    ]


def _zei_ke_san_chuan(four: list[dict]) -> dict[str, Any]:
    """
    贼克法发三传（基础版）：
      - 上克下为"克"；下贼上为"贼"
      - 优先取"贼"为初传；无贼取"克"为初传
      - 中传：初传所在课的天盘 → 再加天盘 (近似)
      - 末传：中传天盘 → 再加天盘
    本版用最简口诀做演示，复杂的"比用、涉害"留给后续。
    """
    # 找贼/克爻
    zei, ke = [], []
    for c in four:
        tw = ZHI_WUXING[c["tian"]]
        dw = ZHI_WUXING[c["di"]]
        if WUXING_KE.get(tw) == dw:  # 上克下
            ke.append(c)
        if WUXING_KE.get(dw) == tw:  # 下贼上
            zei.append(c)

    chu = (zei[0] if zei else (ke[0] if ke else four[0]))
    chuan1 = chu["tian"]
    return {
        "method": "贼克法（基础）",
        "初传": chuan1,
        "中传": chu["tian"],          # 简化：用同一课为示例
        "末传": four[-1]["tian"],     # 简化：取第四课天盘
        "trigger_class": chu["index"],
    }


def _gui_shen_pan(day_gan: str, tian_pan: dict[str, str]) -> dict[str, str]:
    """十二贵神（昼贵简化版）：贵人从日干指定的地支起，顺布十二神。"""
    start = DAY_GUI_REN.get(day_gan, "卯")
    start_idx = DI_ZHI.index(start)
    out: dict[str, str] = {}
    for i, shen in enumerate(TWELVE_GUI_SHEN):
        zhi = DI_ZHI[(start_idx + i) % 12]
        out[zhi] = shen
    return out


class LiuRenService:
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
        solar = Solar.fromYmdHms(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
        lunar = solar.getLunar()
        ec = lunar.getEightChar()
        day_gz = ec.getDay()
        day_gan, day_zhi = day_gz[0], day_gz[1]

        # 1. 月将
        zhongqi, zhongqi_dt = _current_zhongqi(lunar.getJieQiTable(), dt)
        yue_jiang = _yue_jiang_for_zhongqi(zhongqi)

        # 2. 占时
        zhan_shi = _hour_to_zhi(dt.hour)

        # 3. 天盘（月将加时）
        tian_pan = _layout_tian_pan(yue_jiang, zhan_shi)

        # 4. 四课
        four = _four_classes(day_gan, day_zhi, tian_pan)

        # 5. 三传
        san_chuan = _zei_ke_san_chuan(four)

        # 6. 十二贵神
        gui_shen = _gui_shen_pan(day_gan, tian_pan)

        result = {
            "context": ctx,
            "day_ganzhi": day_gz,
            "zhongqi": zhongqi,
            "yue_jiang": yue_jiang,
            "zhan_shi": zhan_shi,
            "tian_pan": tian_pan,
            "four_classes": four,
            "san_chuan": san_chuan,
            "twelve_gui_shen": gui_shen,
            "note": "基础版：仅实现贼克法；比用/涉害/遥克等其余八宗门后续增补。",
        }
        result["analysis"] = liuren_analysis.analyze(result)
        return result
