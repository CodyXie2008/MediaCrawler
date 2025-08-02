from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.config import router as config_router
from api.crawler import router as crawler_router

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)

app.include_router(config_router)
app.include_router(crawler_router) 