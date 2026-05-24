from fastapi import APIRouter, HTTPException, Query

from app.schemas.base import APIResponse
from app.services.jiemeng_service import JieMengService


router = APIRouter()


@router.get("/search", response_model=APIResponse, summary="周公解梦查询")
def search(q: str = Query(..., min_length=1, description="梦境关键字"),
           top_k: int = Query(5, ge=1, le=20)):
    try:
        return APIResponse(data=JieMengService.search(q, top_k=top_k))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/categories", response_model=APIResponse, summary="解梦分类列表")
def categories():
    return APIResponse(data=JieMengService.categories())
