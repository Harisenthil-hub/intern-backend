# app/modules/cylinder/router.py
from fastapi import APIRouter
from app.modules.cylinder.schemas import TrackerCreate
from app.modules.cylinder import service

router = APIRouter(prefix="/tracker",tags=["Location Tracker"])


@router.get("/")
async def get_trackers():
    return await service.get_all_trackers()


@router.post("/")
async def create_tracker(data: TrackerCreate):
    return await service.create_tracker(data)


@router.put("/{id}")
async def update_tracker(id: str, data: TrackerCreate):
    return await service.update_tracker(id, data)


@router.patch("/{id}/post")
async def post_tracker(id: str):
    return await service.post_tracker(id)