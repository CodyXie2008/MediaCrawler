from fastapi import APIRouter, Request
from services.config_service import get_config, save_config

router = APIRouter()

@router.get("/api/config")
def api_get_config():
    return get_config()

@router.post("/api/config")
async def api_save_config(request: Request):
    data = await request.json()
    return save_config(data) 