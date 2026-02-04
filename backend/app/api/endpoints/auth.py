from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.api import deps
from app.core.config import settings
from app.core import security
from app.services.auth_service import AuthService
from typing import Any
import urllib.parse

router = APIRouter()

@router.get("/login")
def login_redirect():
    """
    Redirects the user to Discord OAuth2 login page.
    """
    if not settings.DISCORD_CLIENT_ID or not settings.DISCORD_REDIRECT_URI:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Discord Client ID or Redirect URI not configured."
        )

    params = {
        "client_id": settings.DISCORD_CLIENT_ID,
        "redirect_uri": settings.DISCORD_REDIRECT_URI,
        "response_type": "code",
        "scope": "identify"
    }
    query_string = urllib.parse.urlencode(params)
    discord_auth_url = f"https://discord.com/api/oauth2/authorize?{query_string}"

    return RedirectResponse(url=discord_auth_url)

@router.get("/callback")
async def callback(code: str, db: AsyncSession = Depends(deps.get_db)) -> Any:
    """
    Exchange code for access token, get user info, and return app JWT.
    """
    try:
        access_token = await AuthService.get_discord_token(code)
        discord_user = await AuthService.get_discord_user(access_token)
        user = await AuthService.authenticate_user(db, discord_user)

        # Create app specific access token
        access_token_jwt = security.create_access_token(subject=user.id)

        return {
            "access_token": access_token_jwt,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "username": user.username,
                "avatar_url": user.avatar_url
            }
        }
    except Exception as e:
         raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Authentication failed: {str(e)}"
        )
