"""奇门「用神指引」匹配逻辑测试。"""
from app.services.analysis.qimen_analysis import analyze
from app.services.qimen_service import USHEN_REFERENCE


def _palace(pid, **kw):
    base = {
        "palace": pid, "direction": f"{pid}方", "bagua": "乾",
        "star": "", "gate": None, "spirit": None,
        "tian_pan_gan": "", "di_pan_gan": "",
        "star_luck": "中", "gate_luck": "中",
    }
    base.update(kw)
    return base


def _qimen(overrides=None, ref=None):
    base = {p: _palace(p) for p in range(1, 10)}
    for p in overrides or []:
        base[p["palace"]] = p
    return {
        "ju_label": "阳遁一局",
        "palaces": [base[i] for i in range(1, 10)],
        # orig=2 / now=4：既非伏吟也非反吟，不触发格局
        "zhi_fu_zhi_shi": {
            "zhi_fu_star": "天蓬", "zhi_fu_orig_palace": 2,
            "zhi_fu_now_palace": 4,
            "zhi_shi_gate": "休门", "zhi_shi_now_palace": 6,
        },
        "ushen_reference": ref or USHEN_REFERENCE,
    }


def _line(advices, theme):
    return next((a for a in advices if a.startswith(theme + "：")), "")


def test_marriage_matches_six_he_spirit():
    """婚姻用神是八神「六合」，旧实现拿门去比整串，永远匹配不到。"""
    r = analyze(_qimen([_palace(3, spirit="六合")]))
    line = _line(r["ushen_advice"], "婚姻")
    assert line, r["ushen_advice"]
    assert "六合" in line
    assert "现位 3宫" in line


def test_medicine_matches_tian_xin_star():
    r = analyze(_qimen([_palace(6, star="天心")]))
    line = _line(r["ushen_advice"], "求医")
    assert line
    assert "天心" in line
    assert "现位 6宫" in line


def test_zhi_fu_spelling_matches_spirit():
    """八神常量是「值符」，旧用神表写「直符」，永远不命中。"""
    r = analyze(_qimen([_palace(1, spirit="值符")]))
    line = _line(r["ushen_advice"], "诉讼")
    assert line
    assert "值符" in line
    assert "现位 1宫" in line


def test_token_priority_beats_palace_order():
    """求财优先生门；六合在更小的宫号也不能抢先。"""
    r = analyze(_qimen([_palace(3, spirit="六合"), _palace(9, gate="生门")]))
    line = _line(r["ushen_advice"], "求财")
    assert line
    assert "现位 9宫" in line


def test_gan_qi_lands_on_tian_pan_gan():
    """乙奇落到天盘干「乙」上。"""
    r = analyze(_qimen([_palace(4, tian_pan_gan="乙")]))
    line = _line(r["ushen_advice"], "婚姻")
    assert line
    assert "乙" in line
    assert "现位 4宫" in line


def test_empty_plate_has_no_advice():
    r = analyze(_qimen())
    assert r["ushen_advice"] == []


def test_reference_table_well_formed():
    assert len(USHEN_REFERENCE) >= 15
    for theme, info in USHEN_REFERENCE.items():
        assert info["用神"].strip(), theme
        assert info["宜往"].strip(), theme
