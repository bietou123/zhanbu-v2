from fastapi import APIRouter, HTTPException

from app.schemas.base import BaseBirthInput, APIResponse
from app.services.qizheng_service import QiZhengService


router = APIRouter()


@router.post("/compute", response_model=APIResponse, summary="七政四余星盘")
def compute(payload: BaseBirthInput):
    try:
        data = QiZhengService.compute(
            birth_time=payload.birth_time,
            longitude=payload.longitude, latitude=payload.latitude,
            is_lunar=payload.is_lunar, is_leap_month=payload.is_leap_month,
        )
        return APIResponse(data=data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
