from fastapi import APIRouter, HTTPException

from app.schemas.base import BaseBirthInput, APIResponse
from app.services.xiaoliuren_service import XiaoLiuRenService


router = APIRouter()


@router.post("/compute", response_model=APIResponse, summary="小六壬起课")
def compute(payload: BaseBirthInput):
    try:
        data = XiaoLiuRenService.compute(
            birth_time=payload.birth_time,
            longitude=payload.longitude, latitude=payload.latitude,
            is_lunar=payload.is_lunar, is_leap_month=payload.is_leap_month,
        )
        return APIResponse(data=data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
