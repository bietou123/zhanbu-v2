"""Profile CRUD service."""
from __future__ import annotations

from sqlmodel import select

from app.models.profile import Profile, get_session
from app.schemas.base import BaseBirthInput


class ProfileService:
    @staticmethod
    def list_all() -> list[dict]:
        with get_session() as s:
            rows = s.exec(select(Profile).order_by(Profile.created_at.desc())).all()
            return [r.model_dump() for r in rows]

    @staticmethod
    def create(payload: BaseBirthInput, note: str = "") -> dict:
        with get_session() as s:
            p = Profile(
                name=payload.name,
                gender=payload.gender,
                birth_time=payload.birth_time,
                is_lunar=payload.is_lunar,
                is_leap_month=payload.is_leap_month,
                longitude=payload.longitude,
                latitude=payload.latitude,
                note=note,
            )
            s.add(p)
            s.commit()
            s.refresh(p)
            return p.model_dump()

    @staticmethod
    def get(profile_id: int) -> dict | None:
        with get_session() as s:
            p = s.get(Profile, profile_id)
            return p.model_dump() if p else None

    @staticmethod
    def remove(profile_id: int) -> bool:
        with get_session() as s:
            p = s.get(Profile, profile_id)
            if not p:
                return False
            s.delete(p)
            s.commit()
            return True
