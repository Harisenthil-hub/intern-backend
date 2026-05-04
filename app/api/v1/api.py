# app/api/v1/api.py
from fastapi import APIRouter
from app.modules.dispatch.router import router as dispatch_router
from app.modules.returns.router import router as return_router
from app.modules.cylinder.router import router as tracker_router

# This file collects all module routers into one
api_router = APIRouter()

api_router.include_router(dispatch_router, tags=["Dispatch"])
api_router.include_router(return_router,tags=["Return"])
api_router.include_router(tracker_router, tags=["Tracker"])