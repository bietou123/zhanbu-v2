from fastapi import APIRouter, HTTPException

from app.schemas.base import BaseBirthInput, APIResponse
from app.services.ziwei_service import ZiWeiService


router = APIRouter()


@router.post("/compute", response_model=APIResponse, summary="紫微斗数排盘")
def compute(payload: BaseBirthInput):
    try:
        data = ZiWeiService.compute(
            birth_time=payload.birth_time,
            gender=payload.gender,
            longitude=payload.longitude,
            latitude=payload.latitude,
            is_lunar=payload.is_lunar,
            is_leap_month=payload.is_leap_month,
        )
        return APIResponse(data=data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
