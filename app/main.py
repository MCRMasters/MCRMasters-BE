from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.endpoints import api_router
from app.core.config import settings
from app.schemas.base_response import BaseResponse

app = FastAPI(
    title="MCRMasters-BE",
    description="A FastAPI backend application for MCRMasters",
    version="1.0.0",
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check() -> BaseResponse:
    return BaseResponse(message="healthy")
