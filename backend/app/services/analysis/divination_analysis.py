"""占卜起卦分析层 —— 卦象综合解读"""
from __future__ import annotations
from typing import Any


def analyze(div: dict[str, Any]) -> dict[str, Any]:
    ben = div["ben_gua"]
    bian = div["bian_gua"]
    hu = div["hu_gua"]
    moving = div.get("moving_yao_indexes_bottom_up", [])
    is_changed = ben["name"] != bian["name"]

    summary = (
        f"本卦 {ben['name']}（{ben['upper']} 上 {ben['lower']} 下）"
        + (f"，变卦 {bian['name']}" if is_changed else "，无动爻 (本卦定局)")
    )

    yao_advice = []
    yao_names = ["初爻", "二爻", "三爻", "四爻", "五爻", "上爻"]
    for i in moving:
        yao_advice.append(f"{yao_names[i]}动")

    return {
        "summary": summary,
        "ben_judgement": ben["judgement"],
        "bian_judgement": bian["judgement"] if is_changed else None,
        "hu_judgement": f"互卦 {hu['name']}：{hu['judgement']}",
        "moving_yao": yao_advice,
        "principle": (
            "六爻断法：本卦看事之始；互卦看事之中间隐伏；"
            "变卦看事之归结。动爻多者主变化大，无动爻则事态稳定。"
        ),
        "overall": (
            f"综合断："
            + ("事在变动之中，最终归向变卦之象。" if is_changed
               else "事相已定，依本卦之象论吉凶。")
        ),
    }
