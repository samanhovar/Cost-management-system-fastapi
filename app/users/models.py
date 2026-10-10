from sqlalchemy import Column, Integer, String, DateTime, func, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from core.database import Base

from passlib.context import CryptContext

pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto",
)


class UserModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)

    username = Column(String(250), unique=True, nullable=False)
    password = Column(String, nullable=False)

    is_active = Column(String, nullable=True)

    created_date = Column(DateTime, server_default=func.now())
    updated_date = Column(
        DateTime, server_default=func.now(), server_onupdate=func.now()
    )

    costs = relationship("Cost", back_populates="user")

    def hash_password(self, plain_password: str) -> None:
        return pwd_context.hash(plain_password)

    def verify_password(self, plain_password: str) -> bool:
        return pwd_context.verify(plain_password, self.password)

    def set_password(self, plain_text: str) -> None:
        self.password = self.hash_password(plain_text)


class TokenModel(Base):
    __tablename__ = "tokens"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    token = Column(String, unique=True, nullable=False)
    is_revoked = Column(Boolean, default=False, nullable=False)
    created_date = Column(DateTime, default=func.now(), nullable=False)
    expires_at = Column(DateTime, nullable=False)

    user = relationship("UserModel", uselist=False)
