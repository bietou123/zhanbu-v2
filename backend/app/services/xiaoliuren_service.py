"""
小六壬 (Xiao Liu Ren) —— 诸葛马前课
==========================================
口诀：
  大安(1) 留连(2) 速喜(3) 赤口(4) 小吉(5) 空亡(6)
起课法：
  1. 在"大安"位起正月，顺数月份至生月所在
  2. 在该位起初一，顺数日数至生日所在
  3. 在该位起子时，顺数时辰至生时所在 = 时课
返回三传（月将、日将、时将）。
"""
from __future__ import annotations

from datetime import datetime
from typing import Any

from lunar_python import Solar

from app.utils.calendar_core import CalendarCore


GUA = ["大安", "留连", "速喜", "赤口", "小吉", "空亡"]

GUA_MEANING = {
    "大安": {"五行": "木", "方位": "东方", "色": "青", "断": "身不动时，财喜在前，凡事大吉。"},
    "留连": {"五行": "水", "方位": "北方", "色": "黑", "断": "凡事迟滞，留连不开，宜守不宜进。"},
    "速喜": {"五行": "火", "方位": "南方", "色": "红", "断": "喜事临门，求事速成，行人立至。"},
    "赤口": {"五行": "金", "方位": "西方", "色": "白", "断": "口舌是非，宜谨言慎行，防小人。"},
    "小吉": {"五行": "土", "方位": "中宫", "色": "黄", "断": "凡事和合，小有所成，求财利。"},
    "空亡": {"五行": "土", "方位": "中央", "色": "黄", "断": "凡事空虚，所谋不遂，等待时机。"},
}


def _hour_to_zhi_idx(hour: int) -> int:
    return ((hour + 1) // 2) % 12


def _step(month: int, day: int, hour_zhi_idx: int) -> tuple[str, str, str]:
    """返回 (月将, 日将, 时将)。"""
    # 大安起正月
    m_idx = (month - 1) % 6
    # 月将位起初一
    d_idx = (m_idx + (day - 1)) % 6
    # 日将位起子时
    t_idx = (d_idx + hour_zhi_idx) % 6
    return GUA[m_idx], GUA[d_idx], GUA[t_idx]


class XiaoLiuRenService:
    @classmethod
    def compute(
        cls,
        birth_time: str,
        longitude: float,
        latitude: float,
        is_lunar: bool = True,
        is_leap_month: bool = False,
        **_,
    ) -> dict[str, Any]:
        """
        小六壬通常以"农历月日时"起课。
        若用户传公历，先转农历。
        """
        ctx = CalendarCore.resolve(
            birth_time=birth_time,
            longitude=longitude, latitude=latitude,
            is_lunar=is_lunar, is_leap_month=is_leap_month,
        )
        true_dt = datetime.strptime(
            ctx["true_solar_time"]["true_solar_time"], "%Y-%m-%d %H:%M:%S"
        )
        solar = Solar.fromYmdHms(
            true_dt.year, true_dt.month, true_dt.day,
            true_dt.hour, true_dt.minute, true_dt.second,
        )
        lunar = solar.getLunar()
        lunar_month = abs(lunar.getMonth())
        lunar_day = lunar.getDay()
        hour_zhi_idx = _hour_to_zhi_idx(true_dt.hour)

        m_gua, d_gua, t_gua = _step(lunar_month, lunar_day, hour_zhi_idx)

        return {
            "context": ctx,
            "lunar_month": lunar_month,
            "lunar_day": lunar_day,
            "hour_zhi": ["子","丑","寅","卯","辰","巳","午","未","申","酉","戌","亥"][hour_zhi_idx],
            "san_chuan": {
                "月将": {"gua": m_gua, **GUA_MEANING[m_gua]},
                "日将": {"gua": d_gua, **GUA_MEANING[d_gua]},
                "时将": {"gua": t_gua, **GUA_MEANING[t_gua]},
            },
            "primary": t_gua,  # 以时将为本课主断
            "primary_meaning": GUA_MEANING[t_gua],
        }
