"""奇门格局判定（qimen_patterns.judge）单元测试。"""
from app.services.analysis.qimen_patterns import judge


def _palace(pid, tian="", di="", gate=None):
    return {
        "palace": pid,
        "tian_pan_gan": tian,
        "di_pan_gan": di,
        "gate": gate,
        "direction": f"{pid}方",
    }


def _plate(overrides=None, zhi_fu_orig=1, zhi_fu_now=1, zhi_shi_now=1):
    """构造一张最小可用奇门盘；未覆写的宫位留空，不触发任何格局。"""
    base = {p: _palace(p) for p in range(1, 10)}
    for p in overrides or []:
        base[p["palace"]] = p
    return {
        "palaces": [base[i] for i in range(1, 10)],
        "zhi_fu_zhi_shi": {
            "zhi_fu_orig_palace": zhi_fu_orig,
            "zhi_fu_now_palace": zhi_fu_now,
            "zhi_shi_now_palace": zhi_shi_now,
        },
    }


def _names(result):
    return [p["name"] for p in result["patterns"]]


def test_fu_yin():
    """值符归本宫 → 伏吟。"""
    r = judge(_plate(zhi_fu_orig=3, zhi_fu_now=3))
    assert "伏吟" in _names(r)
    assert r["score_delta"] < 0


def test_fan_yin():
    """值符飞对宫 → 反吟。"""
    r = judge(_plate(zhi_fu_orig=1, zhi_fu_now=9))
    assert "反吟" in _names(r)
    assert "伏吟" not in _names(r)


def test_qing_long_fan_shou():
    """天盘戊加地盘丙 → 青龙返首（吉）。"""
    r = judge(_plate([_palace(4, tian="戊", di="丙")]))
    hit = [p for p in r["patterns"] if p["name"] == "青龙返首"]
    assert len(hit) == 1
    assert hit[0]["type"] == "吉"
    assert hit[0]["palace"] == 4
    assert r["score_delta"] > 0


def test_qing_long_tao_zou_with_flaw():
    """天盘乙加地盘辛：既是凶格青龙逃走，又是三奇得使（古称微疵）。"""
    r = judge(_plate([_palace(7, tian="乙", di="辛")]))
    names = _names(r)
    assert "青龙逃走" in names
    assert "三奇得使" in names
    deshi = [p for p in r["patterns"] if p["name"] == "三奇得使"][0]
    assert "微疵" in deshi["detail"]


def test_san_qi_sheng_dian_and_de_shi():
    """天盘丙临离九 → 三奇升殿；丙加戊 → 飞鸟跌穴 + 三奇得使。"""
    r = judge(_plate([_palace(9, tian="丙", di="戊")]))
    names = _names(r)
    assert "三奇升殿" in names
    assert "飞鸟跌穴" in names
    assert "三奇得使" in names


def test_men_po():
    """休门（水）落离九（火）→ 水克火，门迫。"""
    r = judge(_plate([_palace(9, gate="休门")]))
    assert "门迫" in _names(r)


def test_ru_mu():
    """天盘乙入乾六（戌）→ 入墓。"""
    r = judge(_plate([_palace(6, tian="乙")]))
    assert "入墓" in _names(r)


def test_ji_xing():
    """天盘戊临震三 → 击刑。"""
    r = judge(_plate([_palace(3, tian="戊")]))
    assert "击刑" in _names(r)


def test_center_palace_skipped():
    """中宫不参与外周格局判定。"""
    r = judge(_plate([_palace(5, tian="戊", di="丙", gate="休门")],
                     zhi_fu_orig=2, zhi_fu_now=4))
    assert r["patterns"] == []
    assert "未见" in r["summary"]


def test_empty_plate_summary():
    """既非伏吟也非反吟且无格局时，summary 给出兜底说明。"""
    r = judge(_plate(zhi_fu_orig=2, zhi_fu_now=4))
    assert r["patterns"] == []
    assert r["score_delta"] == 0
    assert "未见" in r["summary"]
