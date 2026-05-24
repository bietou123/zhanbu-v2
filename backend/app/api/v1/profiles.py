from fastapi import APIRouter, HTTPException, Query

from app.schemas.base import BaseBirthInput, APIResponse
from app.services.profile_service import ProfileService


router = APIRouter()


@router.get("", response_model=APIResponse, summary="档案列表")
def list_all():
    return APIResponse(data=ProfileService.list_all())


@router.post("", response_model=APIResponse, summary="保存档案")
def create(payload: BaseBirthInput, note: str = Query("")):
    return APIResponse(data=ProfileService.create(payload, note=note))


@router.get("/{profile_id}", response_model=APIResponse, summary="档案详情")
def get_one(profile_id: int):
    p = ProfileService.get(profile_id)
    if not p:
        raise HTTPException(status_code=404, detail="profile not found")
    return APIResponse(data=p)


@router.delete("/{profile_id}", response_model=APIResponse, summary="删除档案")
def remove(profile_id: int):
    ok = ProfileService.remove(profile_id)
    if not ok:
        raise HTTPException(status_code=404, detail="profile not found")
    return APIResponse(data={"deleted": profile_id})
