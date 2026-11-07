"""奇门遁甲分析层 —— 值符值使吉凶 + 格局判定 + 用神指引"""
from __future__ import annotations
from typing import Any

from app.services.analysis.qimen_patterns import judge


def _luck_score(palace: dict) -> int:
    """单宫吉凶打分：星 + 门 + 神综合。"""
    score = 0
    star_luck = palace.get("star_luck", "中")
    gate_luck = palace.get("gate_luck", "中") or "中"
    spirit = palace.get("spirit") or ""
    scoring = {"大吉": 2, "吉": 1, "小吉": 0.5, "中": 0, "中平": 0,
               "小凶": -0.5, "凶": -1, "大凶": -2}
    score += scoring.get(star_luck, 0)
    score += scoring.get(gate_luck, 0)
    # 八神简易加权：值符/六合/太阴=吉，腾蛇/白虎/玄武=凶
    spirit_bonus = {
        "值符": 1, "六合": 1, "太阴": 1, "九天": 0.5, "九地": 0.5,
        "腾蛇": -1, "白虎": -1, "玄武": -1, "勾陈": -0.5,
    }
    score += spirit_bonus.get(spirit, 0)
    return score


def _parse_ushen(text: str) -> list[str]:
    return [t.strip() for t in str(text or "").split("/") if t.strip()]


def _want_names(token: str) -> list[str]:
    """'乙奇' 落到天盘干 '乙'；其余用神按字面匹配。"""
    if len(token) == 2 and token.endswith("奇"):
        return [token[0]]
    return [token]


def _find_ushen(palaces: list[dict], tokens: list[str]):
    """按用神书写顺序（优先级）找第一个命中的宫位。

    旧实现只拿「门」去比对整串用神，婚姻(六合)、求医(天心) 之类永远匹配不到。
    """
    for token in tokens:
        for want in _want_names(token):
            for p in palaces:
                for key in ("gate", "star", "spirit", "tian_pan_gan"):
                    if p.get(key) == want:
                        return p, want
    return None


def analyze(qimen: dict[str, Any]) -> dict[str, Any]:
    palaces = qimen["palaces"]
    patterns = judge(qimen)

    # 格局按宫位累计，用于修正单宫吉凶排序
    delta_by_palace: dict[int, float] = {}
    for pt in patterns["patterns"]:
        pid = pt.get("palace")
        if pid:
            delta_by_palace[pid] = delta_by_palace.get(pid, 0) + pt["score"]

    scored = [
        {"palace": p, "score": _luck_score(p) + delta_by_palace.get(p["palace"], 0)}
        for p in palaces
    ]
    scored.sort(key=lambda x: x["score"], reverse=True)
    best = scored[0]["palace"]
    worst = scored[-1]["palace"]

    zfzs = qimen["zhi_fu_zhi_shi"]
    summary = (
        f"{qimen['ju_label']}，"
        f"值符{zfzs['zhi_fu_star']}在{zfzs['zhi_fu_now_palace']}宫，"
        f"值使{zfzs['zhi_shi_gate']}在{zfzs['zhi_shi_now_palace']}宫。"
    )

    advices = []
    for theme, info in qimen.get("ushen_reference", {}).items():
        found = _find_ushen(palaces, _parse_ushen(info.get("用神", "")))
        if not found:
            continue
        p, name = found
        advices.append(
            f"{theme}：{info['用神']} → {name} 现位 {p['palace']}宫 ({p['direction']})"
        )

    return {
        "summary": summary,
        "best_palace": {
            "palace": best["palace"],
            "direction": best["direction"],
            "bagua": best["bagua"],
            "compose": f"{best['star']} + {best['gate']} + {best['spirit']}",
            "advice": f"今日最吉方位为 {best['direction']}（第{best['palace']}宫）",
        },
        "worst_palace": {
            "palace": worst["palace"],
            "direction": worst["direction"],
            "compose": f"{worst['star']} + {worst['gate']} + {worst['spirit']}",
            "advice": f"今日避忌方位为 {worst['direction']}（第{worst['palace']}宫）",
        },
        "ushen_advice": advices,
        "patterns": patterns,
        "overall": (
            "奇门以「格局」为重："
            "天门 (开/休/生 + 直符/九天/六合) 见者，事可成；"
            "凶门 (死/惊/伤 + 白虎/玄武) 见者，事多阻。"
        ),
    }
