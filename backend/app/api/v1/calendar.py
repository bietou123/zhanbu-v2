"""
Calendar API —— 历法核心接口
对外暴露：
  POST /api/v1/calendar/resolve   一站式排盘前置（真太阳时 + 公农历 + 干支）
  POST /api/v1/calendar/true_solar_time   仅校准真太阳时
  POST /api/v1/calendar/solar_to_lunar    公历 → 农历
"""
from datetime import datetime

from fastapi import APIRouter, HTTPException

from app.schemas.base import BaseBirthInput, APIResponse
from app.utils.calendar_core import CalendarCore


router = APIRouter()


@router.post("/resolve", response_model=APIResponse, summary="一站式历法解算")
def resolve(payload: BaseBirthInput):
    try:
        data = CalendarCore.resolve(
            birth_time=payload.birth_time,
            longitude=payload.longitude,
            latitude=payload.latitude,
            is_lunar=payload.is_lunar,
            is_leap_month=payload.is_leap_month,
        )
        return APIResponse(data=data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/true_solar_time", response_model=APIResponse, summary="真太阳时校准")
def true_solar_time(payload: BaseBirthInput):
    try:
        dt = datetime.strptime(payload.birth_time, "%Y-%m-%d %H:%M:%S")
        res = CalendarCore.true_solar_time(dt, payload.longitude)
        return APIResponse(data=res.__dict__)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/solar_to_lunar", response_model=APIResponse, summary="公历转农历")
def solar_to_lunar(payload: BaseBirthInput):
    try:
        dt = datetime.strptime(payload.birth_time, "%Y-%m-%d %H:%M:%S")
        return APIResponse(data=CalendarCore.solar_to_lunar(dt))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
