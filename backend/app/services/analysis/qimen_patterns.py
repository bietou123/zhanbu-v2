"""
奇门遁甲格局判定
==================
对已排好的时家转盘奇门盘做规则化格局识别：常见吉格、凶格，以及门迫 / 入墓 /
击刑 / 伏吟 / 反吟。

依据口径（各派小有出入，此处取通行版本并在 docstring 注明）：
  - 十干克应：《烟波钓叟歌》通行口诀
  - 庚加三格：《奇门宝鉴御定》「庚加癸兮为大格，加己为刑格不宜，庚加壬时为上格」
  - 三奇得使：《烟波钓叟歌》「乙逢犬马丙鼠猴，六丁玉女骑龙虎」
      乙 + 己/辛、丙 + 戊/庚、丁 + 壬/癸
    注：乙加辛、丙加庚、丁加癸 三组同时又是凶格（青龙逃走 / 荧入太白 /
    朱雀投江），古称「尚有微疵」，此处吉凶两格同时报出，由使用者参酌。
  - 三奇升殿：乙临震三、丙临离九、丁临兑七
  - 门迫：门克宫（宫克门为「门制」，另有轻重之分，此处只报门迫）
  - 入墓：乙丙戊入戌宫、丁己庚入丑宫、辛壬入辰宫、甲癸入未宫
  - 击刑：戊震三、己坤二、庚艮八、辛离九、壬巽四、癸巽四

本模块只做「识别 + 计分」，不下最终吉凶断语。
"""
from __future__ import annotations

from typing import Any

# ───────────────── 五行基础 ─────────────────

GAN_WUXING = {
    "甲": "木", "乙": "木", "丙": "火", "丁": "火", "戊": "土",
    "己": "土", "庚": "金", "辛": "金", "壬": "水", "癸": "水",
}
PALACE_WUXING = {
    1: "水", 2: "土", 3: "木", 4: "木", 5: "土",
    6: "金", 7: "金", 8: "土", 9: "火",
}
GATE_WUXING = {
    "休门": "水", "生门": "土", "伤门": "木", "杜门": "木",
    "景门": "火", "死门": "土", "惊门": "金", "开门": "金",
}
# A 克 B
WUXING_KE = {"木": "土", "土": "水", "水": "火", "火": "金", "金": "木"}

# 洛书对宫（反吟）
OPPOSITE = {1: 9, 2: 8, 3: 7, 4: 6, 5: 5, 6: 4, 7: 3, 8: 2, 9: 1}

# ───────────────── 格局表 ─────────────────

# (天盘干, 地盘干) → (格局名, 吉凶, 分值, 说明)
GAN_COMBOS = {
    ("戊", "丙"): ("青龙返首", "吉", 2.0, "天盘戊加地盘丙，百事可为，谋望成就。"),
    ("丙", "戊"): ("飞鸟跌穴", "吉", 2.0, "天盘丙加地盘戊，事多顺遂，动而有获。"),
    ("乙", "辛"): ("青龙逃走", "凶", -2.0, "天盘乙加地盘辛，主逃亡、失脱、人走财散。"),
    ("辛", "乙"): ("白虎猖狂", "凶", -2.0, "天盘辛加地盘乙，远行多惊，主客不宁。"),
    ("丁", "癸"): ("朱雀投江", "凶", -1.5, "天盘丁加地盘癸，文书口舌、音信难达。"),
    ("癸", "丁"): ("腾蛇妖矫", "凶", -1.5, "天盘癸加地盘丁，主怪异梦寐、疑心生暗鬼。"),
    ("庚", "丙"): ("太白入荧", "凶", -1.5, "天盘庚加地盘丙，主客俱凶，不宜争强。"),
    ("丙", "庚"): ("荧入太白", "凶", -1.5, "天盘丙加地盘庚，门户破损、防盗防失。"),
    ("庚", "癸"): ("大格", "凶", -2.0, "天盘庚加地盘癸，外部阻隔，宜守不宜攻。"),
    ("庚", "壬"): ("小格（上格）", "凶", -1.5, "天盘庚加地盘壬，方向漂移、计划多变。"),
    ("庚", "己"): ("刑格", "凶", -1.5, "天盘庚加地盘己，官非口舌、内部刑伤。"),
}

# 三奇升殿：奇临本位
SAN_QI_DIAN = {"乙": 3, "丙": 9, "丁": 7}

# 三奇得使
SAN_QI_DE_SHI = {
    ("乙", "己"), ("乙", "辛"),
    ("丙", "戊"), ("丙", "庚"),
    ("丁", "壬"), ("丁", "癸"),
}

# 入墓：天盘干 → 墓宫
GAN_MU_PALACE = {
    "乙": 6, "丙": 6, "戊": 6,   # 戌宫（乾六）
    "丁": 8, "己": 8, "庚": 8,   # 丑宫（艮八）
    "辛": 4, "壬": 4,            # 辰宫（巽四）
    "甲": 2, "癸": 2,            # 未宫（坤二）
}

# 击刑：天盘干 → 刑宫
JI_XING = {"戊": 3, "己": 2, "庚": 8, "辛": 9, "壬": 4, "癸": 4}

MU_NAME = {2: "未", 4: "辰", 6: "戌", 8: "丑"}


def _palace_name(p: int) -> str:
    return f"第{p}宫"


def judge(qimen: dict[str, Any]) -> dict[str, Any]:
    """识别整盘格局，返回 {patterns, ji, xiong, score_delta, summary}。"""
    palaces = qimen["palaces"]
    zfzs = qimen["zhi_fu_zhi_shi"]
    orig = zfzs["zhi_fu_orig_palace"]
    now = zfzs["zhi_fu_now_palace"]
    zhi_shi_palace = zfzs["zhi_shi_now_palace"]

    patterns: list[dict] = []

    def add(name: str, kind: str, score: float, palace: int | None,
            direction: str, detail: str) -> None:
        patterns.append({
            "name": name,
            "type": kind,
            "score": score,
            "palace": palace,
            "direction": direction,
            "detail": detail,
        })

    # ── 全盘伏吟 / 反吟 ──
    if orig == now:
        add("伏吟", "凶", -1.5, now, _palace_name(now),
            "值符归本宫，天盘地盘重合，主静守、事迟、原地踏步。")
    elif OPPOSITE.get(orig) == now:
        add("反吟", "凶", -1.0, now, _palace_name(now),
            "值符飞临对宫，天地盘冲，主反复翻覆、事有来回。")

    for p in palaces:
        pid = p["palace"]
        tian = p.get("tian_pan_gan") or ""
        di = p.get("di_pan_gan") or ""
        gate = p.get("gate")
        direction = p.get("direction") or _palace_name(pid)

        if pid == 5:
            continue  # 中宫无门、不参与外周格局

        # ── 十干克应 ──
        combo = GAN_COMBOS.get((tian, di))
        if combo:
            name, kind, score, detail = combo
            add(name, kind, score, pid, direction,
                f"{direction}：{detail}")

        # ── 三奇升殿 ──
        if SAN_QI_DIAN.get(tian) == pid:
            add("三奇升殿", "吉", 1.5, pid, direction,
                f"{direction}：天盘{tian}奇临本位，主贵人相助、谋为顺遂。")

        # ── 三奇得使 ──
        if (tian, di) in SAN_QI_DE_SHI:
            # 同时命中凶格时标注微疵
            flaw = ""
            if (tian, di) in GAN_COMBOS and GAN_COMBOS[(tian, di)][1] == "凶":
                flaw = "（此格古称有微疵，需吉门助力方佳）"
            add("三奇得使", "吉", 1.5, pid, direction,
                f"{direction}：天盘{tian}奇加地盘{di}，得使可用，主得助力。{flaw}")

        # ── 玉女守门 ──
        if tian == "丁" and pid == zhi_shi_palace:
            add("玉女守门", "吉", 1.0, pid, direction,
                f"{direction}：丁奇与值使同宫，宜和合之谋、私密之事。")

        # ── 门迫：门克宫 ──
        if gate and gate in GATE_WUXING:
            if WUXING_KE.get(GATE_WUXING[gate]) == PALACE_WUXING[pid]:
                add("门迫", "凶", -1.0, pid, direction,
                    f"{direction}：{gate}({GATE_WUXING[gate]})克宫位"
                    f"({PALACE_WUXING[pid]})，门受迫则力不从心、事多阻滞。")

        # ── 入墓 ──
        if GAN_MU_PALACE.get(tian) == pid:
            add("入墓", "凶", -1.0, pid, direction,
                f"{direction}：天盘{tian}入{MU_NAME.get(pid, '')}墓，"
                f"主受困、发挥不出、事难见光。")

        # ── 击刑 ──
        if JI_XING.get(tian) == pid:
            add("击刑", "凶", -1.0, pid, direction,
                f"{direction}：天盘{tian}临刑宫，主刑伤、争执、自招其祸。")

    ji = [x for x in patterns if x["type"] == "吉"]
    xiong = [x for x in patterns if x["type"] == "凶"]
    total = round(sum(x["score"] for x in patterns), 2)

    if not patterns:
        summary = "本盘未见常见吉凶格局，以值符值使与用神宫位为主判断。"
    else:
        ji_names = "、".join(x["name"] for x in ji) or "无"
        xiong_names = "、".join(x["name"] for x in xiong) or "无"
        summary = f"命中吉格：{ji_names}；凶格：{xiong_names}。"

    return {
        "patterns": patterns,
        "ji": ji,
        "xiong": xiong,
        "score_delta": total,
        "summary": summary,
    }
