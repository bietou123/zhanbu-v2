"""
大六壬 (Da Liu Ren) —— 完整九宗门
=========================================
排盘流程：
  1. 取月将（按中气：中气后转月将）
  2. 月将加时（月将加在占时位上 → 地盘对应天盘）
  3. 起四课（日干、日干寄宫、日支、日支阴阳）
  4. 发三传（完整九宗门）
  5. 排十二天将（贵人顺逆按其所乘地盘位）
  6. 旬空 / 旬首 / 遁干 / 课体

九宗门判定顺序（结构优先，与实务排盘软件一致）：
  伏吟(k=0) → 返吟(k=6) → 贼克 → 比用 → 涉害 → 遥克(蒿矢/弹射)
  → 八专(课只2) → 别责(课只3) → 昴星(全备无克)

算法移植自 qigua-app 的 daliuren.js（62 项测试验证过的参考实现），
关键差异：**第一课的克关系用「日干本身的五行」判，不用寄宫五行。**
乙(木)寄辰(土)、丁(火)寄未(土)、戊(土)寄巳(火)、辛(金)寄戌(土)、
癸(水)寄丑(土) 五个干寄宫五行与本气不同，用错会整个三传发用错掉。
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
YUE_JIANG_TABLE = [
    ("雨水", "亥", "登明"), ("春分", "戌", "河魁"), ("谷雨", "酉", "从魁"),
    ("小满", "申", "传送"), ("夏至", "未", "小吉"), ("大暑", "午", "胜光"),
    ("处暑", "巳", "太乙"), ("秋分", "辰", "天罡"), ("霜降", "卯", "太冲"),
    ("小雪", "寅", "功曹"), ("冬至", "丑", "大吉"), ("大寒", "子", "神后"),
]
ZHONG_QI_NAMES = [t[0] for t in YUE_JIANG_TABLE]
ZHI_TO_JIANG_NAME = {t[1]: t[2] for t in YUE_JIANG_TABLE}

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

# 十二天将（顺序固定）
TWELVE_GUI_SHEN = [
    "贵人", "腾蛇", "朱雀", "六合", "勾陈", "青龙",
    "天空", "白虎", "太常", "玄武", "太阴", "天后",
]
JI_JIANG = ["贵人", "青龙", "六合", "太常", "太阴", "天后"]
XIONG_JIANG = ["腾蛇", "朱雀", "勾陈", "天空", "白虎", "玄武"]

# 天乙贵人（昼/夜），与 qigua-app daliuren.js GUI_REN 一致（两项目互校）
DAY_GUI_REN = {
    "甲": "未", "戊": "未", "庚": "丑",  # 甲戊兼牛羊
    "乙": "申", "己": "子",              # 乙己鼠猴乡
    "丙": "酉", "丁": "亥",              # 丙丁猪鸡位
    "壬": "卯", "癸": "巳",              # 壬癸兔蛇藏
    "辛": "午",                          # 六辛逢马虎（昼用午）
}
NIGHT_GUI_REN = {
    "甲": "丑", "乙": "子", "丙": "亥", "丁": "酉",
    "戊": "丑", "己": "申", "庚": "未", "辛": "寅",
    "壬": "巳", "癸": "卯",
}
# 贵人顺行的地盘六位
GUI_SHUN_POS = ["亥", "子", "丑", "寅", "卯", "辰"]

# 三刑 / 自刑（伏吟课中末传取用）
XING = {
    "子": "卯", "卯": "子",
    "寅": "巳", "巳": "申", "申": "寅",
    "丑": "戌", "戌": "未", "未": "丑",
    "辰": "辰", "午": "午", "酉": "酉", "亥": "亥",
}
SELF_XING = ["辰", "午", "酉", "亥"]

# 五合（别责课阳日用）
GAN_HE = {
    "甲": "己", "己": "甲", "乙": "庚", "庚": "乙", "丙": "辛",
    "辛": "丙", "丁": "壬", "壬": "丁", "戊": "癸", "癸": "戊",
}

# 孟仲季（涉害课三格）
MENG = ["寅", "申", "巳", "亥"]
ZHONG = ["子", "午", "卯", "酉"]

# 三合局（驿马/别责课用）
SAN_HE_GROUPS = [("申", "子", "辰"), ("亥", "卯", "未"), ("寅", "午", "戌"), ("巳", "酉", "丑")]

# 昼夜：卯至申为昼（决定昼/夜贵人）
DAY_HOURS = ["卯", "辰", "巳", "午", "未", "申"]


# ───────────────────────── 基础工具 ─────────────────────────

def _add_zhi(a: str, n: int) -> str:
    return DI_ZHI[(DI_ZHI.index(a) + n) % 12]


def _zhi_fwd(a: str, b: str) -> int:
    """从 a 顺行到 b 的步数 (0..11)"""
    return (DI_ZHI.index(b) - DI_ZHI.index(a)) % 12


def _jiazi_index(gz: str) -> int:
    for i in range(60):
        if TIAN_GAN[i % 10] == gz[0] and DI_ZHI[i % 12] == gz[1]:
            return i
    return -1


def _xun(day_gz: str) -> dict[str, Any]:
    """旬首与旬空（非查表，推导）"""
    idx = _jiazi_index(day_gz)
    if idx < 0:
        raise ValueError(f"非法干支组合: {day_gz}")
    day_in_xun = idx % 10
    xun_idx = idx // 10
    shou_zhi = DI_ZHI[(idx - day_in_xun) % 12]
    return {
        "xun_shou": "甲" + shou_zhi,
        "xun_kong": [_add_zhi(shou_zhi, 10), _add_zhi(shou_zhi, 11)],
        "xun_index": xun_idx,
        "day_in_xun": day_in_xun,
    }


def _dun_gan(day_gz: str, z: str):
    """旬遁：某地支在本旬所配天干；空亡支无遁干 → None"""
    xsh = _xun(day_gz)["xun_shou"]
    step = _zhi_fwd(xsh[1], z)
    if step > 9:
        return None
    return TIAN_GAN[step]


def _yi_ma(day_zhi: str) -> str:
    """驿马：日支三合局首支之冲。申子辰→寅 寅午戌→申 巳酉丑→亥 亥卯未→巳"""
    for group in SAN_HE_GROUPS:
        if day_zhi in group:
            return _add_zhi(group[0], 6)
    return "寅"


def _meng_zhong_ji(z: str) -> str:
    if z in MENG:
        return "孟"
    if z in ZHONG:
        return "仲"
    return "季"


def _is_day_time(zhan_shi: str) -> bool:
    return zhan_shi in DAY_HOURS


def _yue_jiang_for_zhongqi(zhongqi: str) -> str:
    for name, jiang, _n in YUE_JIANG_TABLE:
        if name == zhongqi:
            return jiang
    return "亥"


def _hour_to_zhi(hour: int) -> str:
    return DI_ZHI[((hour + 1) // 2) % 12]


def _layout_tian_pan(yue_jiang: str, zhan_shi: str) -> dict[str, str]:
    """
    月将加时：把月将放在占时位上，然后地盘十二支顺布得到天盘。
    返回 {地盘支: 天盘支}；offset k = (月将 - 占时) mod 12
    """
    offset = (DI_ZHI.index(yue_jiang) - DI_ZHI.index(zhan_shi)) % 12
    return {z: _add_zhi(z, offset) for z in DI_ZHI}


# ───────────────────────── 四课 ─────────────────────────

def _four_classes(day_gan: str, day_zhi: str, tian_pan: dict[str, str]) -> list[dict]:
    """
    起四课。一课的下神用**日干**（其五行即日干五行，非寄宫五行），
    二三四课下神用地支。返回的每课含判克关系 is_ke_xia / is_zei_shang
    与涉害归家计数用的地盘位 pan_pos。
    """
    ji_gong = GAN_JI_GONG[day_gan]
    c1_tian = tian_pan[ji_gong]
    c2_tian = tian_pan[c1_tian]
    c3_tian = tian_pan[day_zhi]
    c4_tian = tian_pan[c3_tian]
    raw = [
        {"index": 1, "type": "干上神", "xia": day_gan, "xia_label": day_gan,
         "xia_wuxing": GAN_WUXING[day_gan], "pan_pos": ji_gong, "tian": c1_tian},
        {"index": 2, "type": "干阴神", "xia": c1_tian, "xia_label": c1_tian,
         "xia_wuxing": ZHI_WUXING[c1_tian], "pan_pos": c1_tian, "tian": c2_tian},
        {"index": 3, "type": "支上神", "xia": day_zhi, "xia_label": day_zhi,
         "xia_wuxing": ZHI_WUXING[day_zhi], "pan_pos": day_zhi, "tian": c3_tian},
        {"index": 4, "type": "支阴神", "xia": c3_tian, "xia_label": c3_tian,
         "xia_wuxing": ZHI_WUXING[c3_tian], "pan_pos": c3_tian, "tian": c4_tian},
    ]
    courses = []
    for c in raw:
        c["di"] = c["pan_pos"]          # 向后兼容旧字段
        c["shang"] = c["tian"]          # 向后兼容旧字段
        c["shang_wuxing"] = ZHI_WUXING[c["shang"]]
        c["is_ke_xia"] = (WUXING_KE.get(c["shang_wuxing"]) == c["xia_wuxing"])   # 上克下
        c["is_zei_shang"] = (WUXING_KE.get(c["xia_wuxing"]) == c["shang_wuxing"])  # 下贼上
        c["ke_relation"] = "下贼上" if c["is_zei_shang"] else ("上克下" if c["is_ke_xia"] else "无克")
        courses.append(c)
    return courses


def _dedupe(courses: list[dict]) -> list[dict]:
    """四课去重：同一地盘位+同一上神只算一课（否则误走比用/涉害）。"""
    seen = set()
    out = []
    for c in courses:
        key = (c["pan_pos"], c["shang"])
        if key in seen:
            continue
        seen.add(key)
        out.append(c)
    return out


# ───────────────────────── 涉害深浅 ─────────────────────────

def _she_hai_depth(shang: str, pan_pos: str, k: int) -> dict[str, Any]:
    """
    涉害深浅计数：发用神 S 归本家须顺行 k 步，数途经地盘位中"克 S"的个数。
    分歧：方向(顺/逆)与端点(含起点)的不同，两法结论不同则返回 ambiguous 标记。
    """
    w = ZHI_WUXING[shang]

    def count(direction: int):
        n = 0
        passed = []
        for i in range(k):
            p = _add_zhi(pan_pos, direction * i)
            if WUXING_KE.get(ZHI_WUXING[p]) == w:
                n += 1
                passed.append(p)
        return n, passed

    fwd_n, fwd_passed = count(1)
    bwd_n, bwd_passed = count(-1)
    return {"fwd": fwd_n, "fwd_passed": fwd_passed, "bwd": bwd_n, "bwd_passed": bwd_passed}


# ───────────────────────── 比用 → 涉害 ─────────────────────────

def _pick_bi_yong_then_she_hai(
    candidates: list[dict], ctx: dict, type_label: str
) -> dict[str, Any]:
    day_gan = ctx["day_gan"]
    k = ctx["k"]
    courses = ctx["courses"]
    trace: list[str] = []
    notes: list[str] = []

    # 比用法：取上神阴阳与日干相同者
    day_yy = GAN_YIN_YANG[day_gan]
    bi = [c for c in candidates if ZHI_YIN_YANG[c["shang"]] == day_yy]
    trace.append(
        f"比用：日干 {day_gan}({day_yy})，候选上神 "
        + "、".join(f"{c['shang']}({ZHI_YIN_YANG[c['shang']]})" for c in candidates)
        + f" → 与日干同阴阳者 "
        + ("、".join(c["shang"] for c in bi) if bi else "无")
    )
    if len(bi) == 1:
        return {
            "chu": bi[0]["shang"], "trigger": bi[0],
            "method": "比用法", "ke_ti": "知一课（比用课）",
            "desc": f"{type_label}有多，取与日干比者发用", "trace": trace, "notes": notes,
        }

    # 涉害法
    pool = bi if len(bi) >= 2 else candidates
    if len(bi) >= 2:
        trace.append("比用后仍有多个 → 转涉害法")
    else:
        trace.append("无与日干比者 → 转涉害法")

    depths = [{"c": c, "d": _she_hai_depth(c["shang"], c["pan_pos"], k)} for c in pool]
    for x in depths:
        d = x["d"]
        trace.append(
            f"涉害：{x['c']['shang']} 乘地盘{x['c']['pan_pos']}，顺行归家历 {k} 宫，受克 {d['fwd']} 次"
            + (f"（{'、'.join(d['fwd_passed'])}）" if d["fwd_passed"] else "")
            + f"；逆行算法作 {d['bwd']} 次"
        )

    max_fwd = max(x["d"]["fwd"] for x in depths)
    deep_fwd = [x for x in depths if x["d"]["fwd"] == max_fwd]
    max_bwd = max(x["d"]["bwd"] for x in depths)
    deep_bwd = [x for x in depths if x["d"]["bwd"] == max_bwd]
    same_conclusion = (
        len(deep_fwd) == len(deep_bwd)
        and all(any(x is y for y in deep_bwd) for x in deep_fwd)
    )
    if not same_conclusion:
        notes.append(
            "⚠️ 涉害深浅：顺行算法与逆行算法结论不同（"
            + f"顺行深者 {'、'.join(x['c']['shang'] for x in deep_fwd)}，"
            + f"逆行深者 {'、'.join(x['c']['shang'] for x in deep_bwd)}）。"
            + "本盘按顺行（归本家）取用，另一派会得到不同三传，请自行斟酌。"
        )

    if len(deep_fwd) == 1:
        return {
            "chu": deep_fwd[0]["c"]["shang"], "trigger": deep_fwd[0]["c"],
            "method": "涉害法", "ke_ti": "涉害课",
            "desc": "比用不决，取涉害深者发用", "trace": trace, "notes": notes,
        }

    # 涉害深浅相等 → 孟仲季三格
    trace.append("涉害深浅相等 → 按孟仲季取用")
    meng = [x for x in deep_fwd if _meng_zhong_ji(x["c"]["shang"]) == "孟"]
    if len(meng) >= 1:
        return {
            "chu": meng[0]["c"]["shang"], "trigger": meng[0]["c"],
            "method": "涉害法·见机格", "ke_ti": "涉害课（见机格）",
            "desc": "涉害等，取四孟（寅申巳亥）上神发用", "trace": trace, "notes": notes,
        }
    zhong_li = [x for x in deep_fwd if _meng_zhong_ji(x["c"]["shang"]) == "仲"]
    if len(zhong_li) >= 1:
        return {
            "chu": zhong_li[0]["c"]["shang"], "trigger": zhong_li[0]["c"],
            "method": "涉害法·察微格", "ke_ti": "涉害课（察微格）",
            "desc": "涉害等且无孟，取四仲（子午卯酉）上神发用", "trace": trace, "notes": notes,
        }
    gan_shang = courses[0]
    trace.append("孟仲皆无（皆四季神）→ 缀瑕格，取干上神发用")
    return {
        "chu": gan_shang["shang"], "trigger": gan_shang,
        "method": "涉害法·缀瑕格", "ke_ti": "涉害课（缀瑕格／复等格）",
        "desc": "涉害等且孟仲皆无，取干上神发用", "trace": trace, "notes": notes,
    }


# ───────────────────────── 九宗门发三传 ─────────────────────────

def _chain_from(chu: str, tian: dict[str, str]) -> dict[str, str]:
    """以初传为地盘取上神为中传，中传为地盘取上神为末传。"""
    zhong = tian[chu]
    return {"chu": chu, "zhong": zhong, "mo": tian[zhong]}


def _build_san_chuan(ctx: dict) -> dict[str, Any]:
    """
    九宗门主调度。判定顺序：
      1. 伏吟(k=0)  2. 返吟(k=6)  3. 贼克→比用→涉害  4. 遥克(蒿矢/弹射)
      5. 八专(课2)  6. 别责(课3)  7. 昴星(全备无克)
    """
    day_gan = ctx["day_gan"]
    day_zhi = ctx["day_zhi"]
    k = ctx["k"]
    tian = ctx["tian"]
    di = ctx["di"]
    courses = ctx["courses"]
    notes: list[str] = []

    zei = _dedupe([c for c in courses if c["is_zei_shang"]])
    ke = _dedupe([c for c in courses if c["is_ke_xia"]])
    n_distinct = len(_dedupe(courses))
    is_yang_day = GAN_YIN_YANG[day_gan] == "阳"
    gan_shang = courses[0]["shang"]
    zhi_shang = courses[2]["shang"]

    # ═══════ 1. 伏吟 ═══════
    if k == 0:
        trace = ["月将与占时同支 → 天盘地盘完全重合 = 伏吟"]
        if zei or ke:
            cand = zei if zei else ke
            label = "贼（下贼上）" if zei else "克（上克下）"
            trace.append(
                f"伏吟有{label}：" + "，".join(
                    f"第{c['index']}课 {c['shang']}/{c['xia_label']}" for c in cand
                )
            )
            if len(cand) == 1:
                chu = cand[0]["shang"]
                method = "伏吟·取克"
                ke_ti = "伏吟课（重审）" if zei else "伏吟课（元首）"
            else:
                r = _pick_bi_yong_then_she_hai(cand, ctx, label)
                chu = r["chu"]
                method = "伏吟·" + r["method"]
                ke_ti = "伏吟课（" + r["ke_ti"] + "）"
                trace += r["trace"]
                notes += r["notes"]
        else:
            chu = gan_shang if is_yang_day else zhi_shang
            method = "伏吟·自任" if is_yang_day else "伏吟·自信"
            ke_ti = "伏吟课（自任格）" if is_yang_day else "伏吟课（自信格）"
            trace.append(
                f"伏吟无克，{'刚（阳）日取干上神' if is_yang_day else '柔（阴）日取支上神'} {chu} 发用"
            )

        if chu in SELF_XING:
            zhong = zhi_shang if is_yang_day else gan_shang
            mo = _add_zhi(zhong, 6)
            trace.append(
                f"初传 {chu} 属自刑之支（辰午酉亥），依「自刑则取冲」："
                + f"中传取{'支上神' if is_yang_day else '干上神'} {zhong}，末传取中传之冲 {mo}"
            )
            notes.append(
                "分歧：伏吟遇自刑支时，中末传的取法各家不一。本服务用"
                "「中传取支上/干上神、末传取中传之冲」；另有直接取初传之冲为中传的说法。"
            )
        else:
            zhong = XING[chu]
            mo = XING[zhong]
            trace.append(f"伏吟中末传取刑：中传 = 初传{chu}所刑 = {zhong}，末传 = 中传所刑 = {mo}")
            if mo == zhong:
                mo = _add_zhi(zhong, 6)
                trace.append(f"中传 {zhong} 自刑，末传改取其冲 {mo}")
        notes.append("伏吟：天地盘不动，事多停滞、伏而不发，宜静不宜动。")
        return {"chu": chu, "zhong": zhong, "mo": mo, "method": method,
                "ke_ti": ke_ti, "gate": "伏吟", "trace": trace, "notes": notes}

    # ═══════ 2. 返吟 ═══════
    if k == 6:
        trace = ["月将与占时相冲 → 天盘各支与地盘全冲 = 返吟（反吟）"]
        if zei or ke:
            cand = zei if zei else ke
            label = "贼（下贼上）" if zei else "克（上克下）"
            trace.append(f"返吟有{label} → 依贼克法发用")
            if len(cand) == 1:
                chu = cand[0]["shang"]
                method = "返吟·取克"
                ke_ti = "返吟课（无亲格）"
            else:
                r = _pick_bi_yong_then_she_hai(cand, ctx, label)
                chu = r["chu"]
                method = "返吟·" + r["method"]
                ke_ti = "返吟课（无亲格，" + r["ke_ti"] + "）"
                trace += r["trace"]
                notes += r["notes"]
            c = _chain_from(chu, tian)
            notes.append("返吟：天地盘相冲，事主反覆、去而复返、动荡不安。")
            return {**c, "method": method, "ke_ti": ke_ti,
                    "gate": "返吟", "trace": trace, "notes": notes}
        ma = _yi_ma(day_zhi)
        trace.append(
            f"返吟无克 → 取日支 {day_zhi} 之驿马 {ma} 发用；"
            f"中传取支上神 {zhi_shang}，末传取干上神 {gan_shang}"
        )
        notes.append("返吟：天地盘相冲，事主反覆、去而复返、动荡不安。")
        notes.append("分歧：返吟无克时，也有流派以「初传取驿马之上神」而非驿马本支发用。")
        return {"chu": ma, "zhong": zhi_shang, "mo": gan_shang,
                "method": "返吟·驿马", "ke_ti": "返吟课（无依格／井栏射）",
                "gate": "返吟", "trace": trace, "notes": notes}

    # ═══════ 3. 贼克 → 比用 → 涉害 ═══════
    if zei or ke:
        cand = zei if zei else ke
        is_zei = len(zei) > 0
        label = "贼（下贼上）" if is_zei else "克（上克下）"
        zei_desc = "、" .join(f"第{c['index']}课" for c in zei)
        ke_desc = "、" .join(f"第{c['index']}课" for c in ke)
        trace = [
            f"四课克关系：下贼上 {len(zei)} 个{'（' + zei_desc + '）' if zei else ''}，"
            + f"上克下 {len(ke)} 个{'（' + ke_desc + '）' if ke else ''}",
            f"有贼取贼、无贼取克 → 本盘取 {label}",
        ]
        if len(cand) == 1:
            c0 = cand[0]
            trace.append(f"只一{'贼' if is_zei else '克'}，即以第{c0['index']}课上神 {c0['shang']} 发用")
            c = _chain_from(c0["shang"], tian)
            return {
                **c, "method": "贼克法",
                "ke_ti": "重审课" if is_zei else "元首课",
                "gate": "贼克", "trace": trace,
                "notes": [
                    "重审课：下贼上，事由下起、外来之扰，宜再三审度。"
                    if is_zei else "元首课：上克下，事由上决、尊长主事，多主顺遂。"
                ],
            }
        r = _pick_bi_yong_then_she_hai(cand, ctx, label)
        c = _chain_from(r["chu"], tian)
        return {
            **c, "method": r["method"], "ke_ti": r["ke_ti"],
            "gate": "比用" if r["method"].startswith("比用") else "涉害",
            "trace": trace + r["trace"], "notes": r["notes"],
        }

    # ═══════ 4. 遥克（蒿矢 / 弹射） ═══════
    gan_w = GAN_WUXING[day_gan]
    shen_ke_ri = _dedupe([c for c in courses if WUXING_KE.get(ZHI_WUXING[c["shang"]]) == gan_w])
    ri_ke_shen = _dedupe([c for c in courses if WUXING_KE.get(gan_w) == ZHI_WUXING[c["shang"]]])
    if shen_ke_ri or ri_ke_shen:
        is_hao_shi = len(shen_ke_ri) > 0
        cand = shen_ke_ri if is_hao_shi else ri_ke_shen
        trace = [
            "四课无上下相克 → 转遥克法",
            (f"有上神克日干（神克日）：{'、'.join(c['shang'] for c in cand)} → 蒿矢课"
             if is_hao_shi else
             f"无神克日，有日干克上神（日克神）：{'、'.join(c['shang'] for c in cand)} → 弹射课"),
        ]
        notes2: list[str] = []
        extra = ""
        if len(cand) == 1:
            chu = cand[0]["shang"]
        else:
            day_yy = GAN_YIN_YANG[day_gan]
            bi = [c for c in cand if ZHI_YIN_YANG[c["shang"]] == day_yy]
            trace.append(
                f"遥克有多 → 用比法，与日干 {day_gan}({day_yy}) 同阴阳者："
                + ("、".join(c["shang"] for c in bi) if bi else "无")
            )
            if len(bi) == 1:
                chu = bi[0]["shang"]
            else:
                pool = bi if bi else cand
                chu = pool[0]["shang"]
                extra = "（比法未能定一，本服务取课序在先者）"
                notes2.append(
                    "⚠️ 遥克有多且比法不能决一，本服务取课序在先者发用；"
                    "此情形传统文献少见明文，结论不确定。"
                )
        trace.append(f"初传 = {chu}{extra}")
        c = _chain_from(chu, tian)
        return {
            **c,
            "method": "遥克法·蒿矢" if is_hao_shi else "遥克法·弹射",
            "ke_ti": "蒿矢课" if is_hao_shi else "弹射课",
            "gate": "遥克", "trace": trace,
            "notes": notes2 + [
                "蒿矢课：神克日，如矢自远来，祸自外至而力浅。"
                if is_hao_shi else
                "弹射课：日克神，如弹射远物，事在他方而我主动。"
            ],
        }

    # ═══════ 5. 八专（干支同位，四课只两课） ═══════
    if n_distinct == 2:
        trace = [
            f"日干 {day_gan} 寄宫 {GAN_JI_GONG[day_gan]} 与日支 {day_zhi} 同位 → 四课只得两课 = 八专课"
        ]
        if is_yang_day:
            chu = _add_zhi(gan_shang, 2)
            trace.append(f"刚（阳）日：自干上神 {gan_shang} 顺数三位（含本位）得 {chu} 发用")
        else:
            chu = _add_zhi(courses[3]["shang"], -2)
            trace.append(
                f"柔（阴）日：自第四课上神 {courses[3]['shang']} 逆数三位（含本位）得 {chu} 发用"
            )
        trace.append(f"中末传俱用干上神 {gan_shang}")
        return {
            "chu": chu, "zhong": gan_shang, "mo": gan_shang,
            "method": "八专法", "ke_ti": "八专课（帷薄不修）", "gate": "八专",
            "trace": trace,
            "notes": [
                "⚠️ 八专课的发用细则各家出入较大：本服务用「阳日干上神顺数三位、"
                "阴日第四课上神逆数三位，中末俱用干上神」。另有以支上神起数、"
                "或中末传另取的说法。**未经权威校勘。**",
                "⚠️ 传统称「八专」为八日，但按「干寄宫 == 日支」这一结构判据，"
                "六十甲子中只有 甲寅、丁未、己未、庚申、癸丑 五日成立。"
                "各家所列八日（常含乙卯、辛酉）在标准寄宫表下并不满足此判据，"
                "本服务以结构判据为准。",
                "八专课：干支同宫，人事混杂、内外不分，多主暗昧私情。",
            ],
        }

    # ═══════ 6. 别责（课不备，四课只三课） ═══════
    if n_distinct == 3:
        trace = ["四课去重只得三课（课不备）、无克无遥克 → 别责课"]
        if is_yang_day:
            he_gan = GAN_HE[day_gan]
            he_ji_gong = GAN_JI_GONG[he_gan]
            chu = tian[he_ji_gong]
            trace.append(
                f"刚（阳）日：日干 {day_gan} 五合得 {he_gan}，{he_gan} 寄宫 {he_ji_gong}，"
                f"取其上神 {chu} 发用"
            )
        else:
            chu = _add_zhi(day_zhi, 4)
            trace.append(
                f"柔（阴）日：取日支 {day_zhi} 三合局中前一位（顺行四位）{chu} 发用"
            )
        trace.append(f"中末传俱用干上神 {gan_shang}")
        return {
            "chu": chu, "zhong": gan_shang, "mo": gan_shang,
            "method": "别责法", "ke_ti": "别责课（不备课）", "gate": "别责",
            "trace": trace,
            "notes": [
                "⚠️ 别责课发用有分歧：阳日「取日干合神寄宫之上神」与"
                "「径取该寄宫本支」两说；阴日「日支三合前一位」的\"前\"指顺行"
                "第四位（本服务采用）还是逆行，亦有异说。**未经权威校勘。**",
                "别责课：四课不全，事有欠缺、所求不周，宜别求他途。",
            ],
        }

    # ═══════ 7. 昴星（四课全备而无克无遥克） ═══════
    trace = ["四课全备、无上下克、无遥克 → 昴星课（虚一待用）"]
    if is_yang_day:
        chu = tian["酉"]
        trace.append(
            f"刚（阳）日「仰视」：取地盘酉位之上神 {chu} 发用，"
            f"中传取支上神 {zhi_shang}，末传取干上神 {gan_shang}"
        )
        return {
            "chu": chu, "zhong": zhi_shang, "mo": gan_shang,
            "method": "昴星法·阳仰", "ke_ti": "昴星课（虎视格）", "gate": "昴星",
            "trace": trace,
            "notes": ["昴星课（虎视）：无所取用而虚一待之，事多惊疑、进退失据。"],
        }
    chu = di["酉"]
    trace.append(
        f"柔（阴）日「俯视」：取天盘酉所乘之地盘位 {chu} 发用，"
        f"中传取干上神 {gan_shang}，末传取支上神 {zhi_shang}"
    )
    return {
        "chu": chu, "zhong": gan_shang, "mo": zhi_shang,
        "method": "昴星法·阴俯", "ke_ti": "昴星课（冬蛇掩目格）", "gate": "昴星",
        "trace": trace,
        "notes": ["昴星课（冬蛇掩目）：闭目塞听，事主晦滞、有苦难言。"],
    }


# ───────────────────────── 十二天将 ─────────────────────────

def _gui_shen_pan(day_gan: str, tian_pan: dict[str, str], di_pan: dict[str, str],
                  is_day: bool) -> dict[str, Any]:
    """
    十二天将：按日干+昼夜取贵人所乘天盘支 → 找其所乘地盘位 → 该位在
    亥子丑寅卯辰则顺布、巳午未申酉戌则逆布。
    """
    gui_zhi = (DAY_GUI_REN if is_day else NIGHT_GUI_REN).get(day_gan, "卯")
    pos = di_pan[gui_zhi]
    direction = 1 if pos in GUI_SHUN_POS else -1
    by_di = {}
    for i, shen in enumerate(TWELVE_GUI_SHEN):
        by_di[_add_zhi(pos, direction * i)] = shen
    by_tian = {tian_pan[z]: by_di[z] for z in DI_ZHI}
    return {
        "gui_ren_zhi": gui_zhi,
        "gui_ren_pos": pos,
        "direction": "顺行" if direction == 1 else "逆行",
        "dir_reason": (
            f"贵人 {gui_zhi} 乘地盘 {pos} 位，"
            + ("在亥子丑寅卯辰六位 → 十二将顺布" if direction == 1
               else "在巳午未申酉戌六位 → 十二将逆布")
        ),
        "by_di_pan": by_di,
        "by_tian_pan": by_tian,
    }


# ───────────────────────── 课体 ─────────────────────────

def _build_ke_ti(san_chuan: dict, courses: list[dict], k: int, day_gz: str,
                 tian_jiang: dict, gate: str) -> list[dict]:
    """已实现的课体判定（判据确定、可机械判定）；判据不一者不猜。"""
    list_out: list[dict] = []
    chu, zhong, mo = san_chuan["chu"], san_chuan["zhong"], san_chuan["mo"]
    xun_kong = _xun(day_gz)["xun_kong"]
    xun_shou = _xun(day_gz)["xun_shou"]

    chained = (gate in ("贼克", "比用", "涉害", "遥克", "返吟")
               and _add_zhi(chu, k) == zhong and _add_zhi(zhong, k) == mo)
    if chained:
        if k == 1:
            list_out.append({"name": "进茹课", "why": "三传顺次相连（递进一位），事势渐进。"})
        elif k == 11:
            list_out.append({"name": "退茹课", "why": "三传逆次相连（递退一位），事势渐退。"})
        elif k == 2:
            list_out.append({"name": "顺间传课", "why": "三传顺行隔一位相传。"})
        elif k == 10:
            list_out.append({"name": "逆间传课", "why": "三传逆行隔一位相传。"})
        elif k in (4, 8):
            list_out.append({
                "name": "三传成三合", "tentative": True,
                "why": f"三传 {chu}{zhong}{mo} 隔四位，恰成三合局。",
            })

    if chu == xun_shou[1]:
        list_out.append({
            "name": "六仪课",
            "why": f"初传 {chu} 即本旬旬首（{xun_shou}）之支，谓之六仪，主吉、有贵人扶助。",
        })

    gan_shang = courses[0]["shang"]
    zhi_shang = courses[2]["shang"]
    jiang_of = lambda z: tian_jiang["by_tian_pan"].get(z)  # noqa: E731
    three = [gan_shang, zhi_shang, chu]
    if all(jiang_of(z) in JI_JIANG for z in three):
        list_out.append({
            "name": "三光课", "tentative": True,
            "why": f"干上神 {gan_shang}({jiang_of(gan_shang)})、支上神 {zhi_shang}"
                   f"({jiang_of(zhi_shang)})、初传 {chu}({jiang_of(chu)}) 三者皆乘吉将，"
                   "谓之三光，主事事光明顺遂。",
        })

    kong_list = [(n, z) for n, z in (("初传", chu), ("中传", zhong), ("末传", mo))
                 if z in xun_kong]
    if kong_list:
        list_out.append({
            "name": "三传落空",
            "why": "、".join(f"{n}{z}" for n, z in kong_list)
                   + f" 落本日旬空（{'、'.join(xun_kong)}），所主之事易虚而不实。",
        })

    return list_out


# ───────────────────────── 主入口 ─────────────────────────

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

        # 1. 月将（用 getPrevQi 取上一个中气，正确处理农历年边界）
        #    ⚠️ 不要用 getJieQiTable 遍历: 12 月底的节气会归到上一农历年表，
        #    冬至 2026 会被误认为 2025，导致 2026-12-21 后仍停在"小雪"将。
        prev_qi = lunar.getPrevQi()
        zhongqi = prev_qi.getName() if prev_qi else ZHONG_QI_NAMES[-1]
        yue_jiang = _yue_jiang_for_zhongqi(zhongqi)

        # 2. 占时 + 昼夜
        zhan_shi = _hour_to_zhi(dt.hour)
        is_day = _is_day_time(zhan_shi)

        # 3. 天盘（月将加时）+ 地盘逆映射
        tian_pan = _layout_tian_pan(yue_jiang, zhan_shi)
        k = (DI_ZHI.index(yue_jiang) - DI_ZHI.index(zhan_shi)) % 12
        di_pan = {tian_pan[z]: z for z in DI_ZHI}

        # 4. 四课
        courses = _four_classes(day_gan, day_zhi, tian_pan)

        # 5. 三传（九宗门）
        san_ctx = {
            "day_gan": day_gan, "day_zhi": day_zhi, "k": k,
            "tian": tian_pan, "di": di_pan, "courses": courses,
        }
        sc = _build_san_chuan(san_ctx)

        # 6. 十二天将
        gui_shen = _gui_shen_pan(day_gan, tian_pan, di_pan, is_day)

        # 7. 旬空 / 遁干 / 课体
        xun_info = _xun(day_gz)
        san_chuan_detail = []
        for pos, z in (("初传", sc["chu"]), ("中传", sc["zhong"]), ("末传", sc["mo"])):
            san_chuan_detail.append({
                "pos": pos, "zhi": z,
                "gan": _dun_gan(day_gz, z),
                "jiang": gui_shen["by_tian_pan"].get(z),
                "jiang_name": ZHI_TO_JIANG_NAME.get(z),
                "wuxing": ZHI_WUXING[z],
                "kong": z in xun_info["xun_kong"],
                "di_pos": di_pan[z],
            })
        ke_ti = _build_ke_ti(sc, courses, k, day_gz, gui_shen, sc["gate"])

        san_chuan = {
            "初传": sc["chu"], "中传": sc["zhong"], "末传": sc["mo"],
            "method": sc["method"], "ke_ti": sc["ke_ti"], "gate": sc["gate"],
            "trace": sc["trace"], "notes": sc["notes"],
            "trigger_class": sc.get("trigger", {}).get("index"),
            "detail": san_chuan_detail,
        }

        result = {
            "context": ctx,
            "day_ganzhi": day_gz,
            "zhongqi": zhongqi,
            "yue_jiang": yue_jiang,
            "yue_jiang_detail": {
                "name": ZHI_TO_JIANG_NAME[yue_jiang], "qi": zhongqi,
            },
            "zhan_shi": zhan_shi,
            "day_night": {
                "is_day": is_day,
                "label": "昼占" if is_day else "夜占",
            },
            "pan": {
                "k": k,
                "k_desc": f"月将 {yue_jiang} 加占时 {zhan_shi}，天盘相对地盘顺移 {k} 位",
                "tian": tian_pan,
                "di": di_pan,
                "cells": [
                    {
                        "di": z, "tian": tian_pan[z],
                        "jiang": gui_shen["by_di_pan"][z],
                        "tian_jiang_name": ZHI_TO_JIANG_NAME[tian_pan[z]],
                        "tian_kong": tian_pan[z] in xun_info["xun_kong"],
                    }
                    for z in DI_ZHI
                ],
            },
            "four_classes": courses,
            "san_chuan": san_chuan,
            "twelve_gui_shen": gui_shen["by_di_pan"],   # 向后兼容
            "gui_shen_detail": gui_shen,
            "xun": xun_info,
            "ke_ti": ke_ti,
            "notes": (
                sc["notes"]
                + ["月将采用「中气换将」（雨水后亥将…），另有节换将一派。"]
                + [f"贵人用{'昼' if is_day else '夜'}贵表；六壬贵人昼夜归属各家有出入。"]
            ),
        }
        result["analysis"] = liuren_analysis.analyze(result)
        return result
