from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.auth.schemas import (
    RegisterRequest,
    LoginRequest,
    TokenResponse
)

from app.auth.auth import (
    register_user,
    authenticate_user,
    generate_token
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post(
    "/register",
    response_model=TokenResponse
)
def register(
    request: RegisterRequest,
    db: Session = Depends(get_db)
):

    if request.role not in ["candidate", "recruiter"]:
        raise HTTPException(
            status_code=400,
            detail="Role must be candidate or recruiter"
        )

    user = register_user(
        db=db,
        name=request.name,
        email=request.email,
        password=request.password,
        role=request.role
    )

    if not user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    token = generate_token(user)

    return {
        "access_token": token,
        "token_type": "bearer",
        "role": user.role
    }


@router.post(
    "/login",
    response_model=TokenResponse
)
def login(
    request: LoginRequest,
    db: Session = Depends(get_db)
):

    user = authenticate_user(
        db=db,
        email=request.email,
        password=request.password
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    token = generate_token(user)

    return {
        "access_token": token,
        "token_type": "bearer",
        "role": user.role
    }