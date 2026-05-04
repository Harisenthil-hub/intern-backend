# app/modules/returns/router.py
from fastapi import APIRouter
from app.modules.returns.schemas import ReturnCreate
from app.modules.returns import service

router = APIRouter(prefix="/return", tags=["Returns"])


@router.get("/")
async def get_returns():
    return await service.get_all_returns()

@router.post("/")
async def create_return(data: ReturnCreate):
    return await service.create_return(data)


@router.put("/{id}")
async def update_return(id: str, data: ReturnCreate):
    return await service.update_return(id, data)


@router.patch("/{id}/post")
async def post_return(id: str):
    return await service.post_return(id)