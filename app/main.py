from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.endpoints import api_router
from app.core.config import settings
from app.core.error import MCRDomainError
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


@app.exception_handler(MCRDomainError)
async def mcr_domain_error_handler(
    _request: Request,
    exc: MCRDomainError,
) -> JSONResponse:
    """
    MCRDomainError에 대한 전역 예외 처리 핸들러
    유효성 검사 실패 시 422 Unprocessable Entity 반환
    """
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": exc.message,
            "code": exc.code,
            "error_details": exc.details,
        },
    )
