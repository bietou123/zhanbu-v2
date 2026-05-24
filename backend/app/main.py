from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.v1 import calendar as calendar_api
from app.api.v1 import bazi as bazi_api
from app.api.v1 import ziwei as ziwei_api
from app.api.v1 import qimen as qimen_api
from app.api.v1 import liuren as liuren_api
from app.api.v1 import xiaoliuren as xiaoliuren_api
from app.api.v1 import qizheng as qizheng_api
from app.api.v1 import divination as divination_api
from app.api.v1 import meihua as meihua_api
from app.api.v1 import jiemeng as jiemeng_api
from app.api.v1 import profiles as profiles_api
from app.models.profile import init_db
from app.schemas.base import BaseBirthInput, APIResponse
from app.services.bazi_service import BaZiService
from app.services.ziwei_service import ZiWeiService
from app.services.qimen_service import QiMenService


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="詹卜 · 一站式玄学分析平台 API",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["meta"])
def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
    }


# v1 路由挂载
app.include_router(
    calendar_api.router,
    prefix="/api/v1/calendar",
    tags=["calendar"],
)
app.include_router(bazi_api.router, prefix="/api/v1/bazi", tags=["bazi"])
app.include_router(ziwei_api.router, prefix="/api/v1/ziwei", tags=["ziwei"])
app.include_router(qimen_api.router, prefix="/api/v1/qimen", tags=["qimen"])
app.include_router(liuren_api.router, prefix="/api/v1/liuren", tags=["liuren"])
app.include_router(xiaoliuren_api.router, prefix="/api/v1/xiaoliuren", tags=["xiaoliuren"])
app.include_router(qizheng_api.router, prefix="/api/v1/qizheng", tags=["qizheng"])
app.include_router(divination_api.router, prefix="/api/v1/divination", tags=["divination"])
app.include_router(meihua_api.router, prefix="/api/v1/meihua", tags=["meihua"])
app.include_router(jiemeng_api.router, prefix="/api/v1/jiemeng", tags=["jiemeng"])
app.include_router(profiles_api.router, prefix="/api/v1/profiles", tags=["profiles"])


@app.on_event("startup")
def _startup() -> None:
    init_db()


# ----------- Dashboard 三盘联动聚合端点 -----------
@app.post(
    "/api/v1/dashboard/triple_plate",
    response_model=APIResponse,
    tags=["dashboard"],
    summary="同屏联动：八字 + 紫微 + 奇门 一次取回",
)
def triple_plate(payload: BaseBirthInput):
    """前端 Dashboard 一次请求拿到三盘数据，减少往返。"""
    data = {
        "bazi": BaZiService.compute(
            birth_time=payload.birth_time, gender=payload.gender,
            longitude=payload.longitude, latitude=payload.latitude,
            is_lunar=payload.is_lunar, is_leap_month=payload.is_leap_month,
        ),
        "ziwei": ZiWeiService.compute(
            birth_time=payload.birth_time, gender=payload.gender,
            longitude=payload.longitude, latitude=payload.latitude,
            is_lunar=payload.is_lunar, is_leap_month=payload.is_leap_month,
        ),
        "qimen": QiMenService.compute(
            birth_time=payload.birth_time,
            longitude=payload.longitude, latitude=payload.latitude,
            is_lunar=payload.is_lunar, is_leap_month=payload.is_leap_month,
        ),
    }
    return APIResponse(data=data)
