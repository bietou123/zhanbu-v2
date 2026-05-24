"""Profile service smoke tests."""
import pytest

from app.models.profile import init_db, Profile, get_session
from app.services.profile_service import ProfileService
from app.schemas.base import BaseBirthInput


@pytest.fixture(autouse=True)
def _setup():
    init_db()
    # 清空（仅测试用）
    with get_session() as s:
        for r in s.query(Profile).all():
            s.delete(r)
        s.commit()
    yield


def test_create_list_get_delete():
    payload = BaseBirthInput(
        name="test_user", gender=1, birth_time="1990-05-15 14:30:00",
        is_lunar=False, is_leap_month=False,
        longitude=116.40, latitude=39.90,
    )
    created = ProfileService.create(payload, note="单元测试")
    pid = created["id"]
    assert pid is not None

    lst = ProfileService.list_all()
    assert any(r["id"] == pid for r in lst)

    fetched = ProfileService.get(pid)
    assert fetched["name"] == "test_user"

    assert ProfileService.remove(pid) is True
    assert ProfileService.get(pid) is None
