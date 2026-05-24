"""
QiMen DunJia Service —— 时家奇门遁甲完整转盘
================================================
标准时家奇门转盘流程：
  1. 历法 → 节气 + 阴阳遁判断
  2. 三元定局 (上/中/下元)
  3. 地盘三奇六仪 (戊起 ju 宫，阳遁顺布、阴遁逆布)
  4. **找值符**：时干所在旬的旬首 → 旬首对应的仪 → 仪在地盘的宫 = 值符宫
  5. **天盘干飞**：以"值符宫的天干"为锚，整体旋转使时干飞到值符天盘位置；
                 其余天干按九宫飞行顺序跟随
  6. **八门转 (值使转)**：值使从其本宫（即值符宫的门）起，
                 按时干甲到时干乙差的步数，阳遁顺/阴遁逆移
  7. **八神排**：从值符天盘宫起 (值符 腾蛇 太阴 六合 白虎 玄武 九地 九天)，
                 阳遁顺、阴遁逆
  8. **用神参考**：根据问事类型，给出宜往何宫的建议

参考: 《奇门遁甲秘籍大全》《奇门遁甲统宗大全》转盘奇门派
"""
from __future__ import annotations

from datetime import datetime
from typing import Any

from lunar_python import Solar

from app.utils.calendar_core import CalendarCore
from app.services.analysis import qimen_analysis


# ===== 九宫与方位 =====
PALACE_BAGUA = {
    1: ("坎", "北"), 2: ("坤", "西南"), 3: ("震", "东"), 4: ("巽", "东南"),
    5: ("中", "中"), 6: ("乾", "西北"), 7: ("兑", "西"), 8: ("艮", "东北"), 9: ("离", "南"),
}

# ===== 静态九星 (地盘九星) =====
STATIC_STARS = {
    1: "天蓬", 2: "天芮", 3: "天冲", 4: "天辅",
    5: "天禽", 6: "天心", 7: "天柱", 8: "天任", 9: "天英",
}

# ===== 静态八门 (5 中宫无门，传统寄 2 宫) =====
STATIC_GATES = {
    1: "休门", 2: "死门", 3: "伤门", 4: "杜门",
    5: None,           # 5 寄 2
    6: "开门", 7: "惊门", 8: "生门", 9: "景门",
}

# ===== 八神顺序 =====
EIGHT_SPIRITS = ["值符", "腾蛇", "太阴", "六合", "白虎", "玄武", "九地", "九天"]

# ===== 八门吉凶 =====
GATE_LUCK = {
    "休门": ("吉", "宜休养、谋事、求婚"),
    "生门": ("大吉", "宜求财、谋利、开张"),
    "伤门": ("凶", "宜捕猎、讨债，忌求财"),
    "杜门": ("中平", "宜隐蔽、躲灾，忌出行"),
    "景门": ("小吉", "宜进文书、考试"),
    "死门": ("大凶", "宜吊唁、行刑，忌出行"),
    "惊门": ("凶", "宜诉讼、捕逃，忌远行"),
    "开门": ("大吉", "宜开张、出行、谋事"),
    "死门": ("凶", "宜吊唁、行刑，忌喜事"),
}

# ===== 九星吉凶 =====
STAR_LUCK = {
    "天蓬": ("凶", "贼盗之星"),
    "天任": ("吉", "守静之星"),
    "天冲": ("小吉", "勇武之星"),
    "天辅": ("大吉", "文昌之星"),
    "天禽": ("大吉", "守中之星"),
    "天心": ("大吉", "医药之星"),
    "天柱": ("凶", "破坏之星"),
    "天芮": ("大凶", "病符之星"),
    "天英": ("小吉", "文笔之星"),
}

# ===== 节气 → 局数 (24 节气 × 上中下三元) =====
JIE_QI_JU = {
    "冬至": (1, 7, 4), "小寒": (2, 8, 5), "大寒": (3, 9, 6),
    "立春": (8, 5, 2), "雨水": (9, 6, 3), "惊蛰": (1, 7, 4),
    "春分": (3, 9, 6), "清明": (4, 1, 7), "谷雨": (5, 2, 8),
    "立夏": (4, 1, 7), "小满": (5, 2, 8), "芒种": (6, 3, 9),
    "夏至": (9, 3, 6), "小暑": (8, 2, 5), "大暑": (7, 1, 4),
    "立秋": (2, 5, 8), "处暑": (1, 4, 7), "白露": (9, 3, 6),
    "秋分": (7, 1, 4), "寒露": (6, 9, 3), "霜降": (5, 8, 2),
    "立冬": (6, 9, 3), "小雪": (5, 8, 2), "大雪": (4, 7, 1),
}
YANG_DUN_JIEQI = {
    "冬至", "小寒", "大寒", "立春", "雨水", "惊蛰",
    "春分", "清明", "谷雨", "立夏", "小满", "芒种",
}

# ===== 60 甲子 =====
JIA_ZI_60 = [
    "甲子", "乙丑", "丙寅", "丁卯", "戊辰", "己巳", "庚午", "辛未", "壬申", "癸酉",
    "甲戌", "乙亥", "丙子", "丁丑", "戊寅", "己卯", "庚辰", "辛巳", "壬午", "癸未",
    "甲申", "乙酉", "丙戌", "丁亥", "戊子", "己丑", "庚寅", "辛卯", "壬辰", "癸巳",
    "甲午", "乙未", "丙申", "丁酉", "戊戌", "己亥", "庚子", "辛丑", "壬寅", "癸卯",
    "甲辰", "乙巳", "丙午", "丁未", "戊申", "己酉", "庚戌", "辛亥", "壬子", "癸丑",
    "甲寅", "乙卯", "丙辰", "丁巳", "戊午", "己未", "庚申", "辛酉", "壬戌", "癸亥",
]

# ===== 旬首与仪 表 =====
# 60甲子分 6 旬，每旬 10 个干支；旬首甲下面的"仪"是 戊己庚辛壬癸
# 甲子旬 (0-9)  → 戊
# 甲戌旬 (10-19) → 己
# 甲申旬 (20-29) → 庚
# 甲午旬 (30-39) → 辛
# 甲辰旬 (40-49) → 壬
# 甲寅旬 (50-59) → 癸
def _xun_yi(hour_ganzhi: str) -> str:
    """返回时干所属旬对应的仪。"""
    idx = JIA_ZI_60.index(hour_ganzhi)
    return ["戊", "己", "庚", "辛", "壬", "癸"][idx // 10]


# ===== 三奇六仪布序 =====
# 阳遁顺布、阴遁逆布；起点戊。
LIU_YI_SAN_QI = ["戊", "己", "庚", "辛", "壬", "癸", "丁", "丙", "乙"]

# ===== 60 甲子 → 三元 (上0/中1/下2) =====
def _yuan_index(day_ganzhi: str) -> int:
    """日干支 → 三元位置。符头 (甲己日) 每 5 天一元。"""
    idx = JIA_ZI_60.index(day_ganzhi)
    return (idx // 5) % 3


# ===== 时支落宫 (八门用) =====
ZHI_TO_PALACE = {
    "子": 1, "丑": 8, "寅": 8, "卯": 3, "辰": 4, "巳": 4,
    "午": 9, "未": 2, "申": 2, "酉": 7, "戌": 6, "亥": 6,
}


# ===== 地盘三奇六仪 =====
def _layout_di_pan(ju: int, is_yang: bool) -> dict[int, str]:
    """戊起 ju 宫；阳遁按 1→2→3…顺飞 9 步，阴遁按 9→8→7…逆飞。"""
    di_pan: dict[int, str] = {}
    order = list(range(1, 10)) if is_yang else list(range(9, 0, -1))
    start_pos = order.index(ju)
    for i, label in enumerate(LIU_YI_SAN_QI):
        palace = order[(start_pos + i) % 9]
        di_pan[palace] = label
    return di_pan


# ===== 天盘干飞 =====
def _layout_tian_pan(
    di_pan: dict[int, str], zhi_fu_palace: int, hour_gan_palace: int,
) -> dict[int, str]:
    """
    天盘干飞 (转盘奇门派核心)：
      把"值符宫的天干"看作锚点，整个地盘"旋转"，
      使得"原值符宫的天干"飞到"时干本宫"。
      其余 8 宫天干跟着同样的偏移量飞过来。

    实现: rotation = (时干宫位 - 值符宫位) 在循环序列中的差。
    """
    if zhi_fu_palace == 5 or hour_gan_palace == 5:
        # 中宫寄 2 宫处理
        return dict(di_pan)
    # 使用 1,8,3,4,9,2,7,6 的洛书外周 8 宫顺序做循环
    LO_RING = [1, 8, 3, 4, 9, 2, 7, 6]  # 洛书顺时针外周
    if zhi_fu_palace not in LO_RING or hour_gan_palace not in LO_RING:
        return dict(di_pan)

    src = LO_RING.index(zhi_fu_palace)
    dst = LO_RING.index(hour_gan_palace)
    offset = (dst - src) % 8

    tian_pan: dict[int, str] = {5: di_pan.get(5, "")}
    for i, palace in enumerate(LO_RING):
        # 原本在 palace 上的地盘干，现在飞到 LO_RING[(i+offset) % 8]
        new_palace = LO_RING[(i + offset) % 8]
        tian_pan[new_palace] = di_pan[palace]
    return tian_pan


# ===== 八门转 =====
def _layout_gates(
    static_gates: dict[int, str | None], zhi_shi_orig_palace: int,
    hour_zhi_palace: int, is_yang: bool,
) -> dict[int, str | None]:
    """
    八门转：值使（原门）从其本宫 (zhi_shi_orig_palace) 起，
    按 时支宫 (hour_zhi_palace) 推算步数，
    阳遁顺、阴遁逆移动 8 门。
    中宫 5 始终无门。
    """
    LO_RING = [1, 8, 3, 4, 9, 2, 7, 6] if is_yang else [1, 6, 7, 2, 9, 4, 3, 8]
    # 没在外周的不动 (中宫)
    if zhi_shi_orig_palace not in LO_RING:
        return dict(static_gates)
    if hour_zhi_palace not in LO_RING:
        hour_zhi_palace = zhi_shi_orig_palace

    src = LO_RING.index(zhi_shi_orig_palace)
    dst = LO_RING.index(hour_zhi_palace)
    offset = (dst - src) % 8

    gates_out: dict[int, str | None] = {5: None}
    for i, palace in enumerate(LO_RING):
        new_palace = LO_RING[(i + offset) % 8]
        gates_out[new_palace] = static_gates.get(palace)
    return gates_out


# ===== 九星转 =====
def _layout_stars(
    static_stars: dict[int, str], zhi_fu_palace: int,
    hour_gan_palace: int,
) -> dict[int, str]:
    """九星跟着值符走，旋转量同天盘干飞。"""
    if zhi_fu_palace == 5 or hour_gan_palace == 5:
        return dict(static_stars)
    LO_RING = [1, 8, 3, 4, 9, 2, 7, 6]
    if zhi_fu_palace not in LO_RING or hour_gan_palace not in LO_RING:
        return dict(static_stars)

    src = LO_RING.index(zhi_fu_palace)
    dst = LO_RING.index(hour_gan_palace)
    offset = (dst - src) % 8

    stars_out: dict[int, str] = {5: static_stars[5]}  # 天禽固守中宫
    for i, palace in enumerate(LO_RING):
        new_palace = LO_RING[(i + offset) % 8]
        stars_out[new_palace] = static_stars[palace]
    return stars_out


# ===== 八神排布 =====
def _layout_spirits(zhi_fu_palace: int, is_yang: bool) -> dict[int, str]:
    """
    八神从值符宫起，阳遁顺、阴遁逆；中宫 5 跳过。
    """
    LO_RING = [1, 8, 3, 4, 9, 2, 7, 6] if is_yang else [1, 6, 7, 2, 9, 4, 3, 8]
    if zhi_fu_palace not in LO_RING:
        # 中宫值符特殊，简化置于 8 宫
        zhi_fu_palace = 8
    start = LO_RING.index(zhi_fu_palace)
    spirits: dict[int, str] = {5: None}  # 中宫无神
    for i, shen in enumerate(EIGHT_SPIRITS):
        palace = LO_RING[(start + i) % 8]
        spirits[palace] = shen
    return spirits


# ===== 用神参考 =====
USHEN_REFERENCE = {
    "求财": {"用神": "生门 / 太阴 / 六合", "宜往": "生门所在宫"},
    "婚姻": {"用神": "六合 / 天喜", "宜往": "六合所在宫"},
    "出行": {"用神": "开门 / 休门", "宜往": "开门所在宫"},
    "考试": {"用神": "景门 / 天辅", "宜往": "景门或天辅所在宫"},
    "诉讼": {"用神": "开门 / 直符 / 太阴", "宜往": "直符所在宫"},
    "求医": {"用神": "天心 / 开门", "宜往": "天心所在宫"},
    "谋职": {"用神": "开门 / 直符", "宜往": "开门所在宫"},
    "避祸": {"用神": "杜门 / 太阴 / 九地", "宜往": "杜门所在宫"},
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
        dt = datetime.strptime(
            ctx["true_solar_time"]["true_solar_time"], "%Y-%m-%d %H:%M:%S"
        )
        solar = Solar.fromYmdHms(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
        lunar = solar.getLunar()
        ec = lunar.getEightChar()

        # 1. 节气
        jq_table = lunar.getJieQiTable()
        current_jieqi, current_jieqi_dt = None, None
        for name, jq_solar in jq_table.items():
            jq_dt = datetime(
                jq_solar.getYear(), jq_solar.getMonth(), jq_solar.getDay(),
                jq_solar.getHour(), jq_solar.getMinute(),
            )
            if jq_dt <= dt and name in JIE_QI_JU:
                if current_jieqi_dt is None or jq_dt > current_jieqi_dt:
                    current_jieqi, current_jieqi_dt = name, jq_dt
        if current_jieqi is None:
            current_jieqi = "冬至"

        # 2. 阴阳遁
        is_yang = current_jieqi in YANG_DUN_JIEQI

        # 3. 定局
        day_ganzhi = ec.getDay()
        yuan = _yuan_index(day_ganzhi)
        ju = JIE_QI_JU[current_jieqi][yuan]

        # 4. 地盘
        di_pan = _layout_di_pan(ju, is_yang)

        # 5. 时干 + 旬首仪
        hour_ganzhi = ec.getTime()
        hour_gan, hour_zhi = hour_ganzhi[0], hour_ganzhi[1]
        xun_yi = _xun_yi(hour_ganzhi)  # 当前旬的"仪"

        # 6. 值符宫 = 旬仪在地盘的位置
        zhi_fu_palace = next(p for p, g in di_pan.items() if g == xun_yi)

        # 7. 时干本宫 = 时干在地盘的位置 (即时干所在的"仪/奇"宫)
        # 但时干可能不在地盘 (因为地盘只有 戊己庚辛壬癸+丁丙乙 9 个)
        # 时干天盘位置 = 在地盘找时干字符所在宫
        if hour_gan in di_pan.values():
            hour_gan_palace = next(p for p, g in di_pan.items() if g == hour_gan)
        else:
            # 时干为甲，甲不上盘，用旬仪所在的值符宫
            hour_gan_palace = zhi_fu_palace

        # 8. 值使宫 = 值符宫对应的门 (静态)；若值符宫=5 则寄2
        zhi_shi_orig_palace = zhi_fu_palace if zhi_fu_palace != 5 else 2
        zhi_shi_gate = STATIC_GATES[zhi_shi_orig_palace]

        # 9. 时支落宫
        hour_zhi_palace = ZHI_TO_PALACE[hour_zhi]

        # 10. 天盘干飞
        tian_pan = _layout_tian_pan(di_pan, zhi_fu_palace, hour_gan_palace)

        # 11. 九星转 (跟着值符飞)
        stars_dynamic = _layout_stars(STATIC_STARS, zhi_fu_palace, hour_gan_palace)

        # 12. 八门转 (跟着值使飞)
        gates_dynamic = _layout_gates(
            STATIC_GATES, zhi_shi_orig_palace, hour_zhi_palace, is_yang,
        )

        # 13. 八神排布
        spirits = _layout_spirits(hour_gan_palace, is_yang)

        # 14. 整理九宫输出
        palaces_out = []
        for p in range(1, 10):
            bagua, fang = PALACE_BAGUA[p]
            star = stars_dynamic[p]
            gate = gates_dynamic[p]
            star_luck = STAR_LUCK.get(star, ("中", ""))
            gate_luck = GATE_LUCK.get(gate, ("中", "")) if gate else (None, "")
            palaces_out.append({
                "palace": p,
                "bagua": bagua,
                "direction": fang,
                "di_pan_gan": di_pan[p],         # 地盘干
                "tian_pan_gan": tian_pan[p],     # 天盘干
                "star": star,                    # 转盘后九星
                "star_luck": star_luck[0],
                "star_note": star_luck[1],
                "gate": gate,                    # 转盘后八门
                "gate_luck": gate_luck[0],
                "gate_note": gate_luck[1],
                "spirit": spirits[p],            # 八神
                "is_zhi_fu_palace": (p == hour_gan_palace),  # 值符现在所在
                "is_zhi_shi_palace": (p == hour_zhi_palace), # 值使现在所在
            })

        result = {
            "context": ctx,
            "jieqi": current_jieqi,
            "jieqi_time": current_jieqi_dt.strftime("%Y-%m-%d %H:%M:%S")
                if current_jieqi_dt else None,
            "dun": "阳遁" if is_yang else "阴遁",
            "yuan": ["上元", "中元", "下元"][yuan],
            "ju": ju,
            "ju_label": f"{'阳' if is_yang else '阴'}遁{ju}局",
            "day_ganzhi": day_ganzhi,
            "hour_ganzhi": hour_ganzhi,
            "xun_shou_yi": xun_yi,
            "zhi_fu_zhi_shi": {
                "zhi_fu_orig_palace": zhi_fu_palace,
                "zhi_fu_star": STATIC_STARS[zhi_fu_palace],
                "zhi_fu_now_palace": hour_gan_palace,
                "zhi_shi_orig_palace": zhi_shi_orig_palace,
                "zhi_shi_gate": zhi_shi_gate,
                "zhi_shi_now_palace": hour_zhi_palace,
            },
            "palaces": palaces_out,
            "spirits_order": EIGHT_SPIRITS,
            "ushen_reference": USHEN_REFERENCE,
            "note": "时家奇门转盘奇门派：地盘静、天盘飞、九星转、八门转、八神排。",
        }
        result["analysis"] = qimen_analysis.analyze(result)
        return result
