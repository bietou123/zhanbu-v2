"""
紫微斗数分析层 —— 命宫主星 + 关键宫位解读
================================================
"""
from __future__ import annotations
from typing import Any


# 紫微 14 主星个性定位
MAIN_STAR_TRAITS = {
    "紫微": "尊星之首，气质高贵、领导欲强。",
    "天机": "智多星，善谋思辨、能言善道。",
    "太阳": "阳光博爱，正直无私、博施济众。",
    "武曲": "财星武将，果断刚毅、行动力强。",
    "天同": "福星儒雅，性情温和、知足常乐。",
    "廉贞": "次桃花，矛盾复杂、感情细腻。",
    "天府": "财库之主，稳重宽厚、保守安稳。",
    "太阴": "母性慈柔，细腻浪漫、内敛敏感。",
    "贪狼": "桃花欲望，多才多艺、不拘一格。",
    "巨门": "口才之星，言辞犀利、长于辩论。",
    "天相": "印星辅佐，公正务实、勤恳助人。",
    "天梁": "荫星长者，老成持重、济世怀仁。",
    "七杀": "将星孤煞，独立果决、人生跌宕。",
    "破军": "耗星先锋，开创变革、勇于突破。",
}

PALACE_FOCUS = {
    "命宫": "本人性格、命运主调",
    "兄弟": "兄弟手足、合伙关系",
    "夫妻": "婚姻配偶、感情模式",
    "子女": "子女缘分、创造力",
    "财帛": "正财赚取与守财能力",
    "疾厄": "健康体质、潜在疾患",
    "迁移": "外出运、外交人际",
    "交友": "朋友下属、社交圈",
    "官禄": "事业职位、成就",
    "田宅": "不动产、家宅运",
    "福德": "精神享受、寿元福气",
    "父母": "父母缘分、长辈关系",
}


def _palace_stars_desc(stars: list) -> str:
    if not stars:
        return "无主星 (借对宫)"
    return " · ".join(s["name"] + (f"({s['si_hua']})" if s.get("si_hua") else "") for s in stars)


def analyze(ziwei: dict[str, Any]) -> dict[str, Any]:
    palaces = {p["name"]: p for p in ziwei["palaces"]}

    # 命宫主星 → 性格
    ming = palaces["命宫"]
    ming_main_stars = [s["name"] for s in ming["stars"] if s["name"] in MAIN_STAR_TRAITS]
    personality = "；".join(MAIN_STAR_TRAITS.get(s, "") for s in ming_main_stars) \
        or "命宫无主星，借对宫迁移宫看人生格调。"

    # 几个关键宫位
    focus_palaces = {}
    for name in ["命宫", "夫妻", "事业 / 官禄", "财帛", "迁移"]:
        canonical = name.split(" / ")[-1] if " / " in name else name
        if canonical in palaces:
            p = palaces[canonical]
            focus_palaces[canonical] = {
                "宫位地支": p["zhi"],
                "宫干支": p["ganzhi"],
                "主星": _palace_stars_desc(p["stars"]),
                "解读重点": PALACE_FOCUS.get(canonical, ""),
            }
        elif canonical == "官禄" and "官禄" in palaces:
            focus_palaces["官禄"] = palaces["官禄"]

    # 四化星
    si_hua = ziwei.get("si_hua", {})

    # 身宫提示
    shen_zhi = ziwei.get("shen_gong", {}).get("zhi")
    shen_hint = f"身宫落于 {shen_zhi}，是人生后半段重心所在。"

    return {
        "summary": (
            f"{ziwei['wu_xing_ju']['name']}，命宫 {ming['ganzhi']}，"
            f"主星：{_palace_stars_desc(ming['stars'])}"
        ),
        "personality": personality,
        "palace_focus": focus_palaces,
        "si_hua_year": (
            f"本年/出生年干四化：禄→{si_hua.get('禄')}、权→{si_hua.get('权')}、"
            f"科→{si_hua.get('科')}、忌→{si_hua.get('忌')}"
        ),
        "shen_gong_hint": shen_hint,
        "career_advice": (
            "事业宫主星显示职业适性；"
            "若官禄宫见紫微/天府/武曲/廉贞，宜稳定大型组织；"
            "见七杀/破军/贪狼，宜创业开拓；"
            "见天机/天梁，宜咨询/教育/医疗。"
        ),
        "love_advice": (
            "夫妻宫主星映射感情模式："
            "紫微太阴主温柔，廉贞贪狼主热烈，"
            "七杀破军主独立，天同天梁主平淡稳定。"
        ),
    }
