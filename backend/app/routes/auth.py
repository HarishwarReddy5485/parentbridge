from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.user import User, UserRole
from app.models.admin import Admin
from app.schemas.auth import LoginRequest, AdminRegisterRequest, TokenResponse, RefreshTokenRequest, CurrentUserResponse
from app.security.password import verify_password, hash_password
from app.security.jwt import create_access_token, create_refresh_token, decode_refresh_token
from app.security.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register-admin", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register_admin(payload: AdminRegisterRequest, db: AsyncSession = Depends(get_db)):
    """Register a new administrator and return immediate JWT authentication tokens."""
    # Check if email is already taken
    existing = await db.execute(select(User).where(User.email == payload.email))
    if existing.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists"
        )

    # Check if employee_id already exists if supplied
    if payload.employee_id:
        existing_emp = await db.execute(select(Admin).where(Admin.employee_id == payload.employee_id))
        if existing_emp.scalars().first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="An admin with this employee ID already exists"
            )

    # 1. Create User
    new_user = User(
        full_name=payload.full_name,
        email=payload.email,
        password_hash=hash_password(payload.password),
        phone=payload.phone,
        role=UserRole.ADMIN,
        is_active=True
    )
    db.add(new_user)
    await db.flush()

    # 2. Create Admin profile
    admin_profile = Admin(
        user_id=new_user.user_id,
        full_name=payload.full_name,
        email=payload.email,
        phone=payload.phone,
        employee_id=payload.employee_id,
        permissions=["all"],
        is_super_admin=True,
        is_active=True
    )
    db.add(admin_profile)
    await db.commit()
    await db.refresh(new_user)

    # 3. Generate tokens
    access_token = create_access_token(data={
        "sub": str(new_user.user_id),
        "email": new_user.email,
        "role": new_user.role.value,
        "name": new_user.full_name
    })
    refresh_token = create_refresh_token(data={
        "sub": str(new_user.user_id),
        "email": new_user.email
    })

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        role=new_user.role,
        user_id=new_user.user_id,
        full_name=new_user.full_name
    )


@router.post("/login", response_model=TokenResponse)
async def login(credentials: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Authenticate user with email/password and return JWT access and refresh tokens."""
    query = select(User).where(User.email == credentials.email, User.is_active == True)
    result = await db.execute(query)
    user = result.scalars().first()

    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Generate access token payload (3-minute lifetime)
    token_payload = {
        "sub": str(user.user_id),
        "email": user.email,
        "role": user.role.value,
        "name": user.full_name
    }
    access_token = create_access_token(data=token_payload)

    # Generate refresh token (7-day lifetime)
    refresh_token = create_refresh_token(data={"sub": str(user.user_id), "email": user.email})

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        role=user.role,
        user_id=user.user_id,
        full_name=user.full_name
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token_endpoint(payload: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    """Exchange a valid refresh token for a newly issued access token and rotated refresh token."""
    decoded = decode_refresh_token(payload.refresh_token)
    if not decoded or "sub" not in decoded:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"}
        )

    user_id_str = decoded["sub"]
    query = select(User).where(User.user_id == user_id_str, User.is_active == True)
    result = await db.execute(query)
    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or account is deactivated"
        )

    # Generate new access token and rotated refresh token
    new_access_token = create_access_token(data={
        "sub": str(user.user_id),
        "email": user.email,
        "role": user.role.value,
        "name": user.full_name
    })
    new_refresh_token = create_refresh_token(data={"sub": str(user.user_id), "email": user.email})

    return TokenResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
        role=user.role,
        user_id=user.user_id,
        full_name=user.full_name
    )


@router.get("/me", response_model=CurrentUserResponse)
async def get_my_profile(current_user: User = Depends(get_current_user)):
    """Retrieve profile of the currently authenticated user."""
    return current_user
