"""
Profile —— 用户档案存储
=============================
使用 SQLModel + SQLite。文件落地 data/zhanbu.db。
"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path

from sqlmodel import SQLModel, Field, create_engine, Session


class Profile(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True, max_length=64)
    gender: int = Field(ge=0, le=1)
    birth_time: str
    is_lunar: bool = False
    is_leap_month: bool = False
    longitude: float
    latitude: float
    note: str = ""
    created_at: datetime = Field(default_factory=datetime.utcnow)


# DB 路径：项目 backend/data/zhanbu.db
DB_DIR = Path(__file__).resolve().parent.parent.parent / "data"
DB_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DB_DIR / "zhanbu.db"

engine = create_engine(
    f"sqlite:///{DB_PATH}",
    echo=False,
    connect_args={"check_same_thread": False},
)


def init_db() -> None:
    SQLModel.metadata.create_all(engine)


def get_session() -> Session:
    return Session(engine)
