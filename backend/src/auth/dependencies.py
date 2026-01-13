"""Authentication dependencies for Phase III chatbot."""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from uuid import UUID
from typing import Optional

from ..core.database import get_session
from ..core.security import verify_token
from ..models.user import User


# HTTP Bearer token scheme
security = HTTPBearer()


async def get_user_from_jwt(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_session),
) -> User:
    """Get authenticated user from JWT token.

    This is the Phase III enhanced version of JWT verification
    specifically for chatbot endpoints. Extracts user_id from JWT
    and returns the full User object.

    Args:
        credentials: HTTP Bearer token from Authorization header
        db: Database session

    Returns:
        Authenticated User object

    Raises:
        HTTPException: 401 if token is invalid or user not found
    """
    token = credentials.credentials
    user_id = verify_token(token)

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Fetch user from database
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


async def get_user_id_from_jwt(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> UUID:
    """Extract user_id from JWT token without database lookup.

    Lightweight version for endpoints that only need the user_id.

    Args:
        credentials: HTTP Bearer token from Authorization header

    Returns:
        User UUID

    Raises:
        HTTPException: 401 if token is invalid
    """
    token = credentials.credentials
    user_id = verify_token(token)

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user_id
