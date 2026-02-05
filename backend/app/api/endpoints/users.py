from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from jose import jwt, JWTError
from app.api import deps
from app.core.config import settings
from app.models.user import User
from app.models.wallet import Wallet
from app.schemas import wallet as wallet_schema

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(deps.get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # Check if user exists in DB
    result = await db.execute(select(User).where(User.id == int(user_id)))
    user = result.scalars().first()
    if user is None:
        raise credentials_exception
    return user


@router.get("/me")
def read_users_me(current_user: User = Depends(get_current_user)):
    """
    Get current user.
    """
    return {
        "id": current_user.id,
        "username": current_user.username,
        "avatar_url": current_user.avatar_url
    }

@router.get("/me/wallet", response_model=wallet_schema.Wallet)
async def read_user_wallet(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(deps.get_db)
):
    """
    Get current user's wallet and balances.
    """
    result = await db.execute(
        select(Wallet).options(selectinload(Wallet.balances)).where(Wallet.user_id == current_user.id)
    )
    wallet = result.scalars().first()

    if not wallet:
        # Create wallet if it doesn't exist
        wallet = Wallet(user_id=current_user.id)
        db.add(wallet)
        await db.commit()
        await db.refresh(wallet)
        # Re-fetch to load relationships properly (though it will be empty)
        result = await db.execute(
            select(Wallet).options(selectinload(Wallet.balances)).where(Wallet.id == wallet.id)
        )
        wallet = result.scalars().first()

    return wallet
