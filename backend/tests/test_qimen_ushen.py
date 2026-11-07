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
    assert r["ushen_detail"] == []
    assert r["ushen_directions"] == []


def test_detail_carries_score_and_grade():
    r = analyze(_qimen([_palace(3, spirit="六合")]))
    d = next(x for x in r["ushen_detail"] if x["theme"] == "婚姻")
    assert d["palace"] == 3
    assert d["hit"] == "六合"
    assert isinstance(d["score"], (int, float))
    assert d["grade"] in {"大吉", "吉", "平", "凶", "大凶"}


def test_good_palace_graded_auspicious():
    """生门(大吉 2) + 天心(大吉 2) + 六合(1) = 5 分 → 大吉。"""
    r = analyze(_qimen([
        _palace(8, gate="生门", gate_luck="大吉",
                star="天心", star_luck="大吉", spirit="六合"),
    ]))
    d = next(x for x in r["ushen_detail"] if x["theme"] == "婚姻")
    assert d["palace"] == 8
    assert d["score"] == 5
    assert d["grade"] == "大吉"


def test_pattern_delta_downgrades_palace():
    """同一吉宫命中凶格「白虎猖狂」(-2.0)，等级由大吉降为吉。

    用辛/乙 而非庚/癸：天盘庚在艮八会同时触发入墓 + 击刑，
    拿它测单一格局会把三档扣分混在一起。
    """
    base = dict(gate="生门", gate_luck="大吉", star="天心", star_luck="大吉")
    plain = analyze(_qimen([_palace(8, **base)]))
    flawed = analyze(_qimen([
        _palace(8, tian_pan_gan="辛", di_pan_gan="乙", **base),
    ]))
    a = next(x for x in plain["ushen_detail"] if x["theme"] == "求财")
    b = next(x for x in flawed["ushen_detail"] if x["theme"] == "求财")
    assert a["grade"] == "大吉"
    assert b["score"] == a["score"] - 2
    assert b["grade"] == "吉"
    assert "白虎猖狂" in b["patterns"]


def test_directions_merge_same_palace():
    r = analyze(_qimen([
        _palace(6, gate="开门", gate_luck="大吉", spirit="六合"),
    ]))
    g = next(x for x in r["ushen_directions"] if x["palace"] == 6)
    # 求财/婚姻/合作(六合) + 出行/谋职/搬迁(开门) 都聚到同一宫
    assert len(g["themes"]) >= 4
    assert "开门" in g["compose"]
    assert "六合" in g["hits"]


def test_directions_sorted_by_score_desc():
    r = analyze(_qimen([
        _palace(1, gate="生门", gate_luck="大吉", star="天心", star_luck="大吉"),
        _palace(7, gate="死门", gate_luck="大凶", spirit="玄武"),
    ]))
    scores = [x["score"] for x in r["ushen_directions"]]
    assert scores == sorted(scores, reverse=True)
    assert r["ushen_directions"][0]["grade"] == "大吉"


def test_direction_patterns_split_by_type():
    """方位卡里吉格/凶格分开装，前端才能分色显示。"""
    r = analyze(_qimen([
        _palace(8, gate="生门", gate_luck="大吉", star="天心", star_luck="大吉",
                tian_pan_gan="辛", di_pan_gan="乙"),
    ]))
    g = next(x for x in r["ushen_directions"] if x["palace"] == 8)
    assert "白虎猖狂" in g["bad_patterns"]
    assert "白虎猖狂" in g["patterns"]
    assert g["good_patterns"] == []


def test_best_flag_at_most_once():
    """is_best 只标记全盘最高分宫，不会重复标。"""
    r = analyze(_qimen([
        _palace(6, gate="开门", gate_luck="大吉", spirit="六合"),
        _palace(1, gate="死门", gate_luck="大凶", spirit="玄武"),
    ]))
    flags = [x["palace"] for x in r["ushen_directions"] if x["is_best"]]
    assert len(flags) <= 1


def test_compose_skips_empty_slots():
    """门/星/神缺失时不能拼出 'None'。"""
    r = analyze(_qimen([_palace(3, gate="生门", gate_luck="大吉")]))
    for key in ("best_palace", "worst_palace"):
        assert "None" not in r[key]["compose"]


def test_reference_table_well_formed():
    assert len(USHEN_REFERENCE) >= 15
    for theme, info in USHEN_REFERENCE.items():
        assert info["用神"].strip(), theme
        assert info["宜往"].strip(), theme
