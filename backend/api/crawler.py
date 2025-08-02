from fastapi import APIRouter, Request
from services.crawler_service import start_crawler, stop_crawler, get_status, get_logs

router = APIRouter()

@router.post("/api/crawler/start")
async def api_start_crawler(request: Request):
    params = await request.json()
    return start_crawler(params)

@router.post("/api/crawler/stop")
def api_stop_crawler():
    return stop_crawler()

@router.get("/api/crawler/status")
def api_status():
    return get_status()

@router.get("/api/crawler/logs")
def api_logs():
    return get_logs() 