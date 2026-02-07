import httpx
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.config import settings
from app.models.user import User
from app.services.user_service import initialize_new_user

class AuthService:
    DISCORD_API_URL = "https://discord.com/api/v10"

    @staticmethod
    async def get_discord_token(code: str) -> str:
        async with httpx.AsyncClient() as client:
            payload = {
                "client_id": settings.DISCORD_CLIENT_ID,
                "client_secret": settings.DISCORD_CLIENT_SECRET,
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": settings.DISCORD_REDIRECT_URI,
            }
            headers = {"Content-Type": "application/x-www-form-urlencoded"}

            response = await client.post(f"{AuthService.DISCORD_API_URL}/oauth2/token", data=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            return data["access_token"]

    @staticmethod
    async def get_discord_user(access_token: str) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"Bearer {access_token}"}
            response = await client.get(f"{AuthService.DISCORD_API_URL}/users/@me", headers=headers)
            response.raise_for_status()
            return response.json()

    @staticmethod
    async def authenticate_user(db: AsyncSession, discord_user_data: Dict[str, Any]) -> User:
        discord_id_str = discord_user_data["id"]
        user_id = int(discord_id_str)
        username = discord_user_data.get("username")
        avatar = discord_user_data.get("avatar")

        # Construct avatar URL
        avatar_url = None
        if avatar:
            avatar_url = f"https://cdn.discordapp.com/avatars/{discord_id_str}/{avatar}.png"

        # Check if user exists
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalars().first()

        is_new_user = False
        if not user:
            # Create new user
            user = User(
                id=user_id,
                username=username,
                avatar_url=avatar_url
            )
            db.add(user)
            is_new_user = True
        else:
            # Update existing user info
            user.username = username
            user.avatar_url = avatar_url

        if is_new_user:
            await initialize_new_user(user, db)

        await db.commit()
        await db.refresh(user)
        return user
