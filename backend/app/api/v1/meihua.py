from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.schemas.base import BaseBirthInput, APIResponse
from app.services.meihua_service import MeiHuaService


router = APIRouter()


class CharsInput(BaseModel):
    part1: str = Field(..., min_length=1, description="第一段文字（上卦）")
    part2: str = Field(..., min_length=1, description="第二段文字（下卦）")


class TwoNumbersInput(BaseModel):
    n1: int = Field(..., ge=1, description="上卦数")
    n2: int = Field(..., ge=1, description="下卦数")


@router.post("/by_time", response_model=APIResponse, summary="时间起卦")
def by_time(payload: BaseBirthInput):
    try:
        return APIResponse(data=MeiHuaService.by_time(
            birth_time=payload.birth_time,
            longitude=payload.longitude, latitude=payload.latitude,
            is_lunar=payload.is_lunar, is_leap_month=payload.is_leap_month,
        ))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/by_chars", response_model=APIResponse, summary="字数起卦")
def by_chars(payload: CharsInput):
    try:
        return APIResponse(data=MeiHuaService.by_chars(payload.part1, payload.part2))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/by_numbers", response_model=APIResponse, summary="二数起卦")
def by_numbers(payload: TwoNumbersInput):
    try:
        return APIResponse(data=MeiHuaService.by_numbers(payload.n1, payload.n2))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
