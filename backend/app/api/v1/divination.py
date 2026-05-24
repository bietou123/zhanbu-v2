from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.schemas.base import APIResponse
from app.services.divination_service import DivinationService


router = APIRouter()


class CoinInput(BaseModel):
    seed: int | None = Field(None, description="可选随机种子，便于复现演示")


class NumbersInput(BaseModel):
    n1: int = Field(..., ge=1, description="第一数 → 上卦")
    n2: int = Field(..., ge=1, description="第二数 → 下卦")
    n3: int = Field(..., ge=1, description="第三数 → 动爻位置")


@router.post("/coin", response_model=APIResponse, summary="金钱摇卦")
def by_coin(payload: CoinInput):
    try:
        return APIResponse(data=DivinationService.by_coin(seed=payload.seed))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/numbers", response_model=APIResponse, summary="三数报数起卦")
def by_numbers(payload: NumbersInput):
    try:
        return APIResponse(
            data=DivinationService.by_numbers(payload.n1, payload.n2, payload.n3)
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
