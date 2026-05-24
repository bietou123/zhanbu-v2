"""梅花易数分析层 —— 体用 + 三才综合断"""
from __future__ import annotations
from typing import Any


def analyze(mh: dict[str, Any]) -> dict[str, Any]:
    ti_yong = mh["ti_yong"]
    ben = mh["ben_gua"]
    hu = mh["hu_gua"]
    bian = mh["bian_gua"]

    relation = ti_yong["relation"]
    is_lucky = "吉" in relation and "凶" not in relation

    detailed = []
    if "用生体" in relation:
        detailed.append("外力助内，事得人助、贵人相扶。")
    elif "体生用" in relation:
        detailed.append("内力外耗，需付出方有所得，慎防虚耗。")
    elif "用克体" in relation:
        detailed.append("外力压内，事多阻力、防小人或刑伤。")
    elif "体克用" in relation:
        detailed.append("内力胜外，主动出击则能取胜。")
    elif "比和" in relation:
        detailed.append("内外协调，事顺；若同时为吉卦，则锦上添花。")

    return {
        "summary": (
            f"体卦{ti_yong['ti']['gua']}({ti_yong['ti']['wuxing']}) ⇄ "
            f"用卦{ti_yong['yong']['gua']}({ti_yong['yong']['wuxing']}) → {relation}"
        ),
        "ti_yong_detail": "；".join(detailed),
        "is_lucky": is_lucky,
        "ben_gua_advice": f"本卦 {ben['name']}：{ben['judgement']}",
        "hu_gua_advice": f"互卦 {hu['name']}：发展过程中的隐性力量。",
        "bian_gua_advice": f"变卦 {bian['name']}：事情最终的归宿与转化。",
        "ying_qi_hint": (
            "梅花重应期：以体用五行所属，按生扶/克泄的天时（年月日时）定吉凶发生之期。"
        ),
    }
