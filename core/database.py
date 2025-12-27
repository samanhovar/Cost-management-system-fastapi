from rich.table import Column
from sqlalchemy import create_engine, Integer, String, Float
from sqlalchemy.orm import sessionmaker, declarative_base


SQLALCHEMY_DATABASE_URL = "sqlite:///./database.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) # expired on commit

# create base class for declaring tables
Base = declarative_base()


class Cost(Base):
    __tablename__ = "costs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    amount = Column(Float)
    description = Column(String(256))


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()