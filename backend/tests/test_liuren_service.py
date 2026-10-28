"""大六壬九宗门回归测试。

期望值来自与 qigua-app daliuren.js（62 项测试验证）交叉比对，
288 个日期逐列一致（日干支/月将/占时/k/昼夜/gate/method/课名/三传/课体）。
这里每个宗门抽一个已验证用例作回归锚点。
"""
from app.services.liuren_service import LiuRenService


def _pan(bt):
    return LiuRenService.compute(birth_time=bt, longitude=120, latitude=30)


def _assert_case(bt, expected):
    r = _pan(bt)
    sc = r["san_chuan"]
    assert r["day_ganzhi"] == expected["day_ganzhi"], "日干支"
    assert r["yue_jiang"] == expected["yue_jiang"], "月将"
    assert r["zhan_shi"] == expected["zhan_shi"], "占时"
    assert r["pan"]["k"] == expected["k"], "天盘偏移"
    assert r["day_night"]["label"] == expected["label"], "昼夜"
    assert sc["gate"] == expected["gate"], "宗门"
    assert sc["method"] == expected["method"], "发用方法"
    assert sc["ke_ti"] == expected["ke_ti"], "课名"
    assert sc["初传"] == expected["chu"], "初传"
    assert sc["中传"] == expected["zhong"], "中传"
    assert sc["末传"] == expected["mo"], "末传"
    names = [x["name"] for x in r["ke_ti"]]
    assert names == expected["ke_ti_names"], "课体"


def test_zei_ke():
    _assert_case("2026-01-03 12:00:00", dict(
        day_ganzhi="丁丑", yue_jiang="丑", zhan_shi="午", k=7, label="昼占",
        gate="贼克", method="贼克法", ke_ti="重审课",
        chu="卯", zhong="戌", mo="巳", ke_ti_names=[],
    ))


def test_bi_yong():
    _assert_case("2026-01-11 12:00:00", dict(
        day_ganzhi="乙酉", yue_jiang="丑", zhan_shi="午", k=7, label="昼占",
        gate="比用", method="比用法", ke_ti="知一课（比用课）",
        chu="亥", zhong="午", mo="丑", ke_ti_names=["三光课", "三传落空"],
    ))


def test_she_hai():
    _assert_case("2026-02-27 08:00:00", dict(
        day_ganzhi="壬申", yue_jiang="亥", zhan_shi="辰", k=7, label="昼占",
        gate="涉害", method="涉害法", ke_ti="涉害课",
        chu="午", zhong="丑", mo="申", ke_ti_names=[],
    ))


def test_yao_ke():
    _assert_case("2026-02-27 16:00:00", dict(
        day_ganzhi="壬申", yue_jiang="亥", zhan_shi="申", k=3, label="昼占",
        gate="遥克", method="遥克法·弹射", ke_ti="弹射课",
        chu="巳", zhong="申", mo="亥", ke_ti_names=["三传落空"],
    ))


def test_fu_yin():
    _assert_case("2026-03-27 20:00:00", dict(
        day_ganzhi="庚子", yue_jiang="戌", zhan_shi="戌", k=0, label="夜占",
        gate="伏吟", method="伏吟·自任", ke_ti="伏吟课（自任格）",
        chu="申", zhong="寅", mo="巳", ke_ti_names=["三传落空"],
    ))


def test_fan_yin():
    _assert_case("2026-01-27 12:00:00", dict(
        day_ganzhi="辛丑", yue_jiang="子", zhan_shi="午", k=6, label="昼占",
        gate="返吟", method="返吟·驿马", ke_ti="返吟课（无依格／井栏射）",
        chu="亥", zhong="未", mo="辰", ke_ti_names=["三传落空"],
    ))


def test_ba_zhuan():
    _assert_case("2026-12-11 09:00:00", dict(
        day_ganzhi="己未", yue_jiang="寅", zhan_shi="巳", k=9, label="昼占",
        gate="八专", method="八专法", ke_ti="八专课（帷薄不修）",
        chu="亥", zhong="辰", mo="辰", ke_ti_names=[],
    ))


def test_bie_ze():
    _assert_case("2026-04-27 12:00:00", dict(
        day_ganzhi="辛未", yue_jiang="酉", zhan_shi="午", k=3, label="昼占",
        gate="别责", method="别责法", ke_ti="别责课（不备课）",
        chu="亥", zhong="丑", mo="丑", ke_ti_names=["三传落空"],
    ))


def test_mao_xing():
    _assert_case("2026-01-03 08:00:00", dict(
        day_ganzhi="丁丑", yue_jiang="丑", zhan_shi="辰", k=9, label="昼占",
        gate="昴星", method="昴星法·阴俯", ke_ti="昴星课（冬蛇掩目格）",
        chu="子", zhong="辰", mo="戌", ke_ti_names=[],
    ))


def test_十二月末中气跨年():
    """2026-12-27（冬至后）月将必须为丑，不能误判回小雪(寅)。"""
    _assert_case("2026-12-27 12:00:00", dict(
        day_ganzhi="乙亥", yue_jiang="丑", zhan_shi="午", k=7, label="昼占",
        gate="贼克", method="贼克法", ke_ti="重审课",
        chu="午", zhong="丑", mo="申", ke_ti_names=["三光课", "三传落空"],
    ))
