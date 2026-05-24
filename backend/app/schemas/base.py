from datetime import datetime
from pydantic import BaseModel, Field, field_validator


class BaseBirthInput(BaseModel):
    """
    所有术数模块共享的标准核心入参 (Base Input Schema)。
    任何排盘 API 都应当接受这个结构作为起点。
    """
    name: str = Field(..., description="用户姓名", examples=["张三"])
    gender: int = Field(..., ge=0, le=1, description="1=男, 0=女")
    birth_time: str = Field(
        ...,
        description="出生时间，格式 YYYY-MM-DD HH:MM:SS（公历或农历由 is_lunar 决定）",
        examples=["1990-05-15 14:30:00"],
    )
    is_lunar: bool = Field(False, description="birth_time 是否为农历日期")
    is_leap_month: bool = Field(False, description="若 is_lunar=True，是否为闰月")
    longitude: float = Field(
        ..., ge=-180.0, le=180.0,
        description="出生地经度（东经为正），用于真太阳时校准",
        examples=[116.40],
    )
    latitude: float = Field(
        ..., ge=-90.0, le=90.0,
        description="出生地纬度（北纬为正）",
        examples=[39.90],
    )

    @field_validator("birth_time")
    @classmethod
    def _validate_birth_time(cls, v: str) -> str:
        try:
            datetime.strptime(v, "%Y-%m-%d %H:%M:%S")
        except ValueError as e:
            raise ValueError(
                "birth_time 必须为 'YYYY-MM-DD HH:MM:SS' 格式"
            ) from e
        return v


class APIResponse(BaseModel):
    """统一 API 响应包装。"""
    code: int = 0
    message: str = "ok"
    data: dict | list | None = None
