from urllib.parse import urlencode

import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
)
from app.db.session import get_session
from app.schemas.auth_url_response import AuthUrlResponse
from app.schemas.token_response import TokenResponse
from app.services.auth.google import get_or_create_user

router = APIRouter()


@router.get("/login/google", response_model=AuthUrlResponse)
async def google_login():
    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "consent",
    }

    auth_url = f"{settings.GOOGLE_AUTH_URL}?{urlencode(params)}"
    return AuthUrlResponse(auth_url=auth_url)


@router.get("/login/google/callback", response_model=TokenResponse)
async def google_callback(code: str, session: AsyncSession = Depends(get_session)):
    try:
        # Access 토큰 얻기
        token_data = {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "code": code,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code",
        }

        async with httpx.AsyncClient() as client:
            token_response = await client.post(
                settings.GOOGLE_TOKEN_URL,
                data=token_data,
            )
            token_response.raise_for_status()
            token_info = token_response.json()

            # 사용자 정보 조회
            headers = {"Authorization": f"Bearer {token_info['access_token']}"}
            user_response = await client.get(
                settings.GOOGLE_USER_INFO_URL,
                headers=headers,
            )
            user_response.raise_for_status()
            user_info = user_response.json()

        # DB에서 사용자 조회 또는 생성
        user, is_new_user = await get_or_create_user(session, user_info)

        # JWT 토큰 생성
        access_token = create_access_token(data={"sub": user.email})
        refresh_token = create_refresh_token(data={"sub": user.email})

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            is_new_user=is_new_user,
        )

    except httpx.HTTPError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to get token from Google",
        )
