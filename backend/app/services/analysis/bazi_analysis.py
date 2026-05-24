"""
八字分析层 —— 规则化解读
=================================
输入：BaZiService.compute 的完整结果
输出：5 个解读段落
  1. 五行平衡 + 喜用神
  2. 日主性格
  3. 事业格局
  4. 感情婚姻
  5. 财运 / 健康
"""
from __future__ import annotations
from typing import Any


# 日主十干性格
DAY_MASTER_TRAITS = {
    "甲": "甲木参天，性格正直挺拔、有领袖气质，缺点是固执不易变通。",
    "乙": "乙木如花草藤蔓，柔韧温和、善于变通，缺点是优柔寡断。",
    "丙": "丙火太阳，热情开朗、光明磊落，缺点是急躁张扬。",
    "丁": "丁火灯烛，温柔细腻、富有同情心，缺点是敏感多疑。",
    "戊": "戊土如山岳，稳重诚信、有承担力，缺点是固执保守。",
    "己": "己土如田园，包容温和、滋养万物，缺点是优柔多虑。",
    "庚": "庚金如刀斧，果断刚毅、行动力强，缺点是过于直接。",
    "辛": "辛金如珠玉，精致重情、注重美感，缺点是敏感骄傲。",
    "壬": "壬水如江河，聪明机变、思维流畅，缺点是不够稳定。",
    "癸": "癸水如雨露，细腻内敛、富有智慧，缺点是消极退缩。",
}

# 喜用神方位
WUXING_DIRECTION = {
    "金": "西方 / 西北", "木": "东方 / 东南",
    "水": "北方", "火": "南方", "土": "中央 / 西南 / 东北",
}
WUXING_COLOR = {
    "金": "白色 / 银色", "木": "绿色 / 青色",
    "水": "黑色 / 蓝色", "火": "红色 / 紫色", "土": "黄色 / 棕色",
}

# 五行生克
WUXING_SHENG = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
WUXING_KE = {"木": "土", "土": "水", "水": "火", "火": "金", "金": "木"}


def _detect_xi_yong(day_wuxing: str, wuxing_count: dict[str, int]) -> dict:
    """
    简化版喜用神判断：
      若日主太弱 (本气 ≤ 2) → 取生扶 (印比) 为用
      若日主太强 (本气 ≥ 5) → 取耗泄克 (食伤财官) 为用
      中和 (3-4)        → 取调候之神
    """
    me = wuxing_count.get(day_wuxing, 0)
    if me <= 2:
        # 弱：取生我 + 同我
        sheng_me = next(k for k, v in WUXING_SHENG.items() if v == day_wuxing)
        return {
            "judgement": f"日主偏弱（{day_wuxing}={me}）",
            "xi_yong_shen": [sheng_me, day_wuxing],
            "ji_shen": [WUXING_SHENG[day_wuxing], WUXING_KE[day_wuxing]],
            "advice": f"宜补{sheng_me}和{day_wuxing}，避免{WUXING_KE[day_wuxing]}过旺",
        }
    elif me >= 5:
        # 强：取我克 + 克我 + 我生
        ke_me = WUXING_KE[day_wuxing]  # 我克
        wait = WUXING_SHENG[day_wuxing]  # 我生（泄秀）
        return {
            "judgement": f"日主偏旺（{day_wuxing}={me}）",
            "xi_yong_shen": [wait, ke_me],
            "ji_shen": [day_wuxing],
            "advice": f"宜泄秀（生{wait}）或制衡（{ke_me}）",
        }
    else:
        return {
            "judgement": f"日主中和（{day_wuxing}={me}），五行平衡",
            "xi_yong_shen": [day_wuxing],
            "ji_shen": [],
            "advice": "格局平衡，可顺势而为；具体调候依季节定",
        }


def _shi_shen_summary(ten_gods: dict[str, str]) -> str:
    """根据天干十神组合做事业倾向初步判定。"""
    gans = [v for k, v in ten_gods.items() if v != "日主"]
    out = []
    if "正官" in gans or "七杀" in gans:
        out.append("命带官杀，宜从政、管理、纪律性强的行业")
    if "正财" in gans or "偏财" in gans:
        out.append("命带财星，宜经商、贸易、金融")
    if "正印" in gans or "偏印" in gans:
        out.append("命带印星，宜学术、文化、教育")
    if "食神" in gans or "伤官" in gans:
        out.append("命带食伤，宜文艺、技术、创新行业")
    if "比肩" in gans or "劫财" in gans:
        out.append("比劫为重，宜合伙、独立创业（防口舌竞争）")
    return "；".join(out) or "格局以日主为主"


def analyze(bazi: dict[str, Any]) -> dict[str, Any]:
    day_master = bazi["day_master"]
    day_gan = day_master["gan"]
    day_wuxing = day_master["wuxing"]
    wuxing_count = bazi["wuxing_count"]

    xi_yong = _detect_xi_yong(day_wuxing, wuxing_count)
    personality = DAY_MASTER_TRAITS.get(day_gan, "")
    career = _shi_shen_summary(bazi["ten_gods"]["gan"])

    # 大运提示
    next_yun = bazi["da_yun"][0] if bazi.get("da_yun") else None
    next_yun_text = (
        f"目前/即将走的大运是 {next_yun['ganzhi']}（{next_yun['start_year']}-{next_yun['end_year']}），"
        f"对应{next_yun['start_age']}-{next_yun['end_age']}岁。"
        if next_yun else ""
    )

    return {
        "summary": (
            f"日主{day_gan}{day_master['yin_yang']}{day_wuxing}。"
            f"{xi_yong['judgement']}。"
        ),
        "wuxing_balance": {
            **xi_yong,
            "auspicious_directions": [WUXING_DIRECTION[w] for w in xi_yong["xi_yong_shen"]],
            "auspicious_colors": [WUXING_COLOR[w] for w in xi_yong["xi_yong_shen"]],
        },
        "personality": personality,
        "career": career,
        "love": (
            "夫妻宫 (日支) 是配偶宫位。"
            + ("日支与日干天合地合者，配偶有助。" if day_wuxing else "")
        ),
        "wealth_health": (
            f"以{WUXING_KE.get(day_wuxing, '')}为正/偏财，"
            f"忌{xi_yong.get('ji_shen', [])}过旺；"
            f"健康注意{day_wuxing}对应脏腑（"
            f"{ {'木':'肝胆','火':'心小肠','土':'脾胃','金':'肺大肠','水':'肾膀胱'}[day_wuxing] }）调养。"
        ),
        "current_yun_hint": next_yun_text,
    }
