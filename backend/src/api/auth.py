"""Authentication endpoints for user registration and login."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from datetime import datetime

from ..core.database import get_session
from ..core.security import get_password_hash, verify_password, create_access_token
from ..models import User
from ..schemas.user import UserCreate, UserLogin, UserResponse, TokenResponse
from ..api.deps import get_current_user


router = APIRouter()


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_session),
):
    """Register a new user account.

    Args:
        user_data: User registration data (email and password)
        db: Database session

    Returns:
        TokenResponse with access token and user data

    Raises:
        HTTPException: 400 if email already exists
    """
    # Check if email already exists (case-insensitive)
    result = await db.execute(
        select(User).where(User.email == user_data.email.lower())
    )
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Validate password strength (minimum 8 chars, at least one letter and one number)
    password = user_data.password
    if len(password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters long"
        )
    if not any(c.isalpha() for c in password) or not any(c.isdigit() for c in password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must contain at least one letter and one number"
        )

    # Create new user
    hashed_password = get_password_hash(password)
    new_user = User(
        email=user_data.email.lower(),
        hashed_password=hashed_password,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    # Generate JWT token
    access_token = create_access_token(new_user.id)

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(new_user)
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: UserLogin,
    db: AsyncSession = Depends(get_session),
):
    """Authenticate user and return JWT token.

    Args:
        credentials: User login credentials (email and password)
        db: Database session

    Returns:
        TokenResponse with access token and user data

    Raises:
        HTTPException: 401 if credentials are invalid
    """
    # Find user by email (case-insensitive)
    result = await db.execute(
        select(User).where(User.email == credentials.email.lower())
    )
    user = result.scalar_one_or_none()

    # Verify user exists and password is correct
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Generate JWT token
    access_token = create_access_token(user.id)

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(user)
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
):
    """Get current authenticated user information.

    Args:
        current_user: The authenticated user from JWT token

    Returns:
        UserResponse with current user data
    """
    return UserResponse.model_validate(current_user)
