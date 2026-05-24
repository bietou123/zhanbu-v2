"""大六壬分析层 —— 三传断事"""
from __future__ import annotations
from typing import Any


# 12 地支吉凶简释
ZHI_TRAITS = {
    "子": "智慧机变，主流通", "丑": "蓄藏滞缓，主财库",
    "寅": "刚健发动，主官职", "卯": "条达升发，主车马门户",
    "辰": "天罗，主官非斗讼", "巳": "文明智慧，主信息",
    "午": "光明显达，主名声", "未": "退藏隐微，主酒食",
    "申": "刑伤变动，主驿马", "酉": "肃杀整齐，主刀剑",
    "戌": "地网，主奴仆争斗", "亥": "潜伏蓄养，主孕育",
}


def analyze(liuren: dict[str, Any]) -> dict[str, Any]:
    sc = liuren["san_chuan"]
    chu, zhong, mo = sc["初传"], sc["中传"], sc["末传"]

    return {
        "summary": (
            f"月将 {liuren['yue_jiang']} 加 {liuren['zhan_shi']}，"
            f"三传：{chu} → {zhong} → {mo}"
        ),
        "chu_chuan": {
            "ganzhi": chu,
            "断": f"初传{chu}主事之始：{ZHI_TRAITS.get(chu, '')}",
        },
        "zhong_chuan": {
            "ganzhi": zhong,
            "断": f"中传{zhong}主事之中：{ZHI_TRAITS.get(zhong, '')}",
        },
        "mo_chuan": {
            "ganzhi": mo,
            "断": f"末传{mo}主事之终：{ZHI_TRAITS.get(mo, '')}",
        },
        "principle": (
            "壬学口诀：初传定事由，中传定经过，末传定结局。"
            "三传相生为顺，相克为逆；空亡则事多虚。"
        ),
        "gui_shen_hint": (
            "十二贵神中，贵人/六合/太常临三传则吉，"
            "白虎/玄武/腾蛇/勾陈临之则凶。"
        ),
    }
