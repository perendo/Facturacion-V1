import os

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User
from ..schemas.auth import RegisterRequest, LoginRequest, TokenResponse, UserRead
from ..services.auth_service import hash_password, verify_password, create_access_token
from ..dependencies import get_current_user
from ..rate_limit import check_rate_limit

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, request: Request, db: Session = Depends(get_db)):
    check_rate_limit(request, "register")
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    user = User(
        email=payload.email,
        hashed_password=hash_password(payload.password),
        full_name=payload.full_name,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, request: Request, response: Response, db: Session = Depends(get_db)):
    check_rate_limit(request, "login")
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = create_access_token(str(user.id))
    environment = os.getenv("ENVIRONMENT", os.getenv("APP_ENV", "development")).lower()
    response.set_cookie(
        key="token",
        value=token,
        httponly=True,
        secure=environment in {"production", "prod"},
        samesite="lax",
        max_age=60 * 60 * 24,
        path="/",
    )
    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserRead)
def me(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(response: Response):
    environment = os.getenv("ENVIRONMENT", os.getenv("APP_ENV", "development")).lower()
    response.delete_cookie(key="token", path="/", secure=environment in {"production", "prod"}, samesite="lax", httponly=True)
    return None