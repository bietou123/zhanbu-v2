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


def _grade(score: float) -> str:
    """单宫综合分 → 五级吉凶（与门/星吉凶口径一致）。"""
    if score >= 3:
        return "大吉"
    if score >= 1.5:
        return "吉"
    if score > -1:
        return "平"
    if score > -2.5:
        return "凶"
    return "大凶"


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
    details: list[dict] = []
    for theme, info in qimen.get("ushen_reference", {}).items():
        found = _find_ushen(palaces, _parse_ushen(info.get("用神", "")))
        if not found:
            continue
        p, name = found
        advices.append(
            f"{theme}：{info['用神']} → {name} 现位 {p['palace']}宫 ({p['direction']})"
        )
        details.append({
            "theme": theme,
            "want": info["用神"],
            "hit": name,
            "palace": p["palace"],
            "direction": p["direction"],
            "gate": p.get("gate") or "",
            "star": p.get("star") or "",
            "spirit": p.get("spirit") or "",
        })

    # 单宫综合分（门/星/神 + 格局修正），用于给用神落点定吉凶
    palace_score = {
        sc["palace"]["palace"]: sc["score"] for sc in scored
    }
    pattern_names: dict[int, list[str]] = {}
    good_by_palace: dict[int, list[str]] = {}
    bad_by_palace: dict[int, list[str]] = {}
    for pt in patterns["patterns"]:
        pid = pt.get("palace")
        if not pid:
            continue
        pattern_names.setdefault(pid, []).append(pt["name"])
        bucket = bad_by_palace if pt.get("type") == "凶" else good_by_palace
        bucket.setdefault(pid, []).append(pt["name"])

    for d in details:
        score = round(palace_score.get(d["palace"], 0.0), 2)
        d["score"] = score
        d["grade"] = _grade(score)
        d["patterns"] = pattern_names.get(d["palace"], [])
        d["good_patterns"] = good_by_palace.get(d["palace"], [])
        d["bad_patterns"] = bad_by_palace.get(d["palace"], [])

    # 按宫位聚合：同一方位适合办哪几件事，按吉凶排序
    merged: dict[int, dict] = {}
    for d in details:
        g = merged.setdefault(d["palace"], {
            "palace": d["palace"],
            "direction": d["direction"],
            "score": d["score"],
            "grade": d["grade"],
            "compose": " + ".join(
                x for x in (d["star"], d["gate"], d["spirit"]) if x
            ) or "—",
            "patterns": d["patterns"],
            "good_patterns": d["good_patterns"],
            "bad_patterns": d["bad_patterns"],
            "themes": [],
            "hits": [],
        })
        if d["theme"] not in g["themes"]:
            g["themes"].append(d["theme"])
        if d["hit"] and d["hit"] not in g["hits"]:
            g["hits"].append(d["hit"])

    ushen_directions = sorted(
        merged.values(),
        key=lambda x: (x["score"], len(x["themes"])),
        reverse=True,
    )
    # 标记是否就是全盘最高分宫（与 best_palace 对照，避免两处说法打架）
    for g in ushen_directions:
        g["is_best"] = g["palace"] == best["palace"]

    def _compose(p: dict) -> str:
        return " + ".join(x for x in (p.get("star"), p.get("gate"), p.get("spirit")) if x) or "—"

    return {
        "summary": summary,
        "best_palace": {
            "palace": best["palace"],
            "direction": best["direction"],
            "bagua": best["bagua"],
            "compose": _compose(best),
            "advice": f"今日最吉方位为 {best['direction']}（第{best['palace']}宫）",
        },
        "worst_palace": {
            "palace": worst["palace"],
            "direction": worst["direction"],
            "compose": _compose(worst),
            "advice": f"今日避忌方位为 {worst['direction']}（第{worst['palace']}宫）",
        },
        "ushen_advice": advices,
        "ushen_detail": details,
        "ushen_directions": ushen_directions,
        "patterns": patterns,
        "overall": (
            "奇门以「格局」为重："
            "天门 (开/休/生 + 直符/九天/六合) 见者，事可成；"
            "凶门 (死/惊/伤 + 白虎/玄武) 见者，事多阻。"
        ),
    }
