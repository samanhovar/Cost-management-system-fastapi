from typing import Annotated

from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from fastapi.responses import JSONResponse

from core.database import get_db
from core.config import settings

from sqlalchemy.orm import Session

from users.models import UserModel, TokenModel
from users.schemas import UserLoginSchema, UserRegisterSchema

from auth.jwt_auth import (
    generate_access_token,
    generate_refresh_token,
    set_auth_cookies,
    clear_auth_cookies,
)

router = APIRouter(tags=["users"], prefix="/users")


@router.post("/login")
async def user_login(
    request: UserLoginSchema,
    response: Response,
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

    db_token = TokenModel(
        user_id=user_obj.id,
        token=refresh_token,
        expires_at=datetime.utcnow() + timedelta(settings.REFRESH_TOKEN_EXPIRE_SECONDS),
    )
    db.add(db_token)
    db.commit()

    response = JSONResponse({"message": "logged in successfully"})

    # send tokens by cookies
    set_auth_cookies(
        response=response, access_token=access_token, refresh_token=refresh_token
    )

    return response


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
    request: Request,
    db: Annotated[Session, Depends(get_db)],
):
    incoming_token = request.cookies.get("refresh_token")
    if not incoming_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token missing",
        )

    db_token = db.query(TokenModel).filter(TokenModel.token == incoming_token).first()
    if not db_token or db_token.is_revoked or db_token.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    db_token.is_revoked = True

    new_access_token = generate_access_token(user_id=db_token.user_id)
    new_refresh_token = generate_refresh_token(user_id=db_token.user_id)

    new_db_token = TokenModel(
        user_id=db_token.user_id,
        token=new_refresh_token,
        expires_at=datetime.utcnow() + timedelta(settings.REFRESH_TOKEN_EXPIRE_SECONDS),
    )
    db.add(new_db_token)
    db.commit()

    response = JSONResponse({"message": "token refreshed successfully"})
    set_auth_cookies(
        response=response,
        access_token=new_access_token,
        refresh_token=new_refresh_token,
    )

    return response


# Deleting cookies in logout
@router.post("/logout")
async def user_logout(
    request: Request,
    db: Annotated[Session, Depends(get_db)],
):
    incoming_token = request.cookies.get("refresh_token")
    if incoming_token:
        db_token = (
            db.query(TokenModel).filter(TokenModel.token == incoming_token).first()
        )
        if db_token:
            db_token.is_revoked = True
            db.commit()

    response = JSONResponse({"message": "logged out successfully"})
    clear_auth_cookies(response=response)
    
    return response
