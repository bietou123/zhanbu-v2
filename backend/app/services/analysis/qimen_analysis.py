"""奇门遁甲分析层 —— 值符值使吉凶 + 用神指引"""
from __future__ import annotations
from typing import Any


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


def analyze(qimen: dict[str, Any]) -> dict[str, Any]:
    palaces = qimen["palaces"]
    scored = [{"palace": p, "score": _luck_score(p)} for p in palaces]
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
        # 找含有 "生门" 的宫等
        for p in palaces:
            if p.get("gate") and p["gate"] in info["用神"]:
                advices.append(
                    f"{theme}：{info['用神']} → 现位 {p['palace']}宫 ({p['direction']})"
                )
                break

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
        "overall": (
            "奇门以「格局」为重："
            "天门 (开/休/生 + 直符/九天/六合) 见者，事可成；"
            "凶门 (死/惊/伤 + 白虎/玄武) 见者，事多阻。"
        ),
    }
