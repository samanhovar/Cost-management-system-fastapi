from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse

from core.database import get_db

from sqlalchemy.orm import Session

from users.models import UserModel
from users.schemas import UserLoginSchema, UserRegisterSchema, UserRefreshTokenSchema

from auth.jwt_auth import (
    generate_access_token,
    generate_refresh_token,
    decode_refresh_token,
)

router = APIRouter(tags=["users"], prefix="/users")


@router.post("/login")
async def user_login(
    request: UserLoginSchema,
    db: Annotated[Session, Depends(get_db)],
):
    user_obj = db.query(UserModel).filter_by(username=request.username.lower()).first()
    if not user_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="username or password invalid",
        )

    if not user_obj.verify_password(request.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="username or password invalid",
        )

    # Token
    access_token = generate_access_token(user_obj.id)
    refresh_token = generate_refresh_token(user_obj.id)

    return JSONResponse(
        {
            "message": "logged in successfully",
            "access_token": access_token,
            "refresh_token": refresh_token,
        }
    )


@router.post("/register")
async def user_register(
    request: UserRegisterSchema,
    db: Annotated[Session, Depends(get_db)],
):
    if db.query(UserModel).filter_by(username=request.username.lower()).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="username already exists!",
        )

    user_obj = UserModel(username=request.username.lower())
    user_obj.set_password(request.password)

    db.add(user_obj)
    db.commit()
    return JSONResponse({"detail": "user registered successfully"})


@router.post("/refresh-token")
async def user_refresh_token(
    request: UserRefreshTokenSchema,
    db: Annotated[Session, Depends(get_db)],
):
    user_id = decode_refresh_token(request.token)
    access_token = generate_access_token(user_id)
    return JSONResponse({"access_token": access_token})
