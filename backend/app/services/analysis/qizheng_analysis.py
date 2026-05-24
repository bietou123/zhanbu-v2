"""七政四余分析层 —— 命主星 + 太阳/太阴解读"""
from __future__ import annotations
from typing import Any


# 12 宫解释 (西方占星借用)
ZODIAC_TRAITS = {
    "白羊": ("火 / 始动", "开拓、冲动、领导力"),
    "金牛": ("土 / 固定", "稳重、务实、享受感官"),
    "双子": ("风 / 变动", "聪敏、好奇、善沟通"),
    "巨蟹": ("水 / 始动", "温柔、念家、情感丰富"),
    "狮子": ("火 / 固定", "自信、慷慨、有领袖魅力"),
    "处女": ("土 / 变动", "细致、批判、追求完美"),
    "天秤": ("风 / 始动", "平衡、外交、爱好和谐"),
    "天蝎": ("水 / 固定", "深沉、神秘、洞察力强"),
    "射手": ("火 / 变动", "乐观、探索、爱自由"),
    "摩羯": ("土 / 始动", "踏实、有抱负、责任感强"),
    "水瓶": ("风 / 固定", "独立、创新、人道关怀"),
    "双鱼": ("水 / 变动", "浪漫、敏感、富有想象"),
}

PLANET_TRAITS = {
    "太阳": "自我意志、人生方向",
    "太阴": "情感模式、内在需求",
    "水星": "思维表达、沟通学习",
    "金星": "爱情审美、人际魅力",
    "火星": "行动力、欲望与冲突",
    "木星": "幸运、扩展、信仰",
    "土星": "约束、责任、长期成就",
    "罗睺": "执念、业力之北节点",
    "计都": "解脱、灵性之南节点",
    "月孛": "深层欲望、隐藏面",
    "紫炁": "智慧灵感、贵气",
}


def analyze(qz: dict[str, Any]) -> dict[str, Any]:
    sun = qz["seven_zheng"]["太阳"]
    moon = qz["seven_zheng"]["太阴"]
    venus = qz["seven_zheng"]["金星"]
    mars = qz["seven_zheng"]["火星"]

    def fmt(name, p):
        zd = p["zodiac"]
        traits = ZODIAC_TRAITS.get(zd, ("?", ""))
        return {
            "longitude": p["longitude"],
            "zodiac": zd,
            "xiu": p["xiu"],
            "trait": PLANET_TRAITS.get(name, ""),
            "zodiac_trait": traits[1],
            "element": traits[0],
        }

    return {
        "summary": (
            f"太阳在{sun['zodiac']} {sun['degree']:.1f}°，"
            f"太阴在{moon['zodiac']} {moon['degree']:.1f}°"
        ),
        "sun": fmt("太阳", sun),
        "moon": fmt("太阴", moon),
        "venus": fmt("金星", venus),
        "mars": fmt("火星", mars),
        "four_yu_hint": (
            "罗睺、计都为月之南北交点，象征业力轴线；"
            "月孛主深层欲望，紫炁主灵性贵气。"
            "中国古星命学常以四余宫位辅断祸福。"
        ),
        "advice": (
            "古典星命以太阳为元神、太阴为本命主、"
            "命宫主星（上升）为人生外在表现。"
            "可参考七政庙旺利陷与彼此互照定吉凶。"
        ),
    }
