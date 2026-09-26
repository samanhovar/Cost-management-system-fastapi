from pydantic import BaseModel, Field, field_validator
from typing import Annotated


class UserLoginSchema(BaseModel):
    username: Annotated[
        str, Field(..., max_length=150, description="username of the user")
    ]
    password: Annotated[str, Field(..., description="password of the user")]


class UserRegisterSchema(BaseModel):
    username: Annotated[
        str, Field(..., max_length=150, description="username of the user")
    ]
    password: Annotated[str, Field(..., description="password of the user")]
    confirm_password: Annotated[
        str, Field(..., description="confirm password of the user")
    ]

    @field_validator("confirm_password")
    def check_password_match(cls, confirm_password, validation):
        if not (confirm_password == validation.data.get("password")):
            raise ValueError("password doesn't match")
        return confirm_password


class UserRefreshTokenSchema(BaseModel):
    token: Annotated[str, Field(..., description="refresh token of the user")]
