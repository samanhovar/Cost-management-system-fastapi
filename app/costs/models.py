from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship

from core.database import Base


class Cost(Base):
    __tablename__ = "costs"
    id = Column(Integer, primary_key=True, autoincrement=True)

    user_id = Column(Integer, ForeignKey("users.id"))

    title = Column(String(128), nullable=False)
    amount = Column(Float, nullable=False)
    description = Column(String(512), nullable=True)

    created_date = Column(DateTime, default=func.now(), nullable=False)
    updated_date = Column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=False
    )

    user = relationship("UserModel", back_populates="costs", uselist=False)
