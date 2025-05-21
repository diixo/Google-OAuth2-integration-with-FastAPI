
import os
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Text,
    Index
)


DB_NAME = "db-storage/access.db"
Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, unique=True, nullable=False)
    user_name = Column(String)
    email = Column(String, unique=True, nullable=False)
    first_logged_in = Column(DateTime, default=datetime.utcnow)
    last_accessed = Column(DateTime, default=datetime.utcnow)

    tokens = relationship("AccessToken", back_populates="user", cascade="all, delete")

    __table_args__ = (
        Index("ix_users_email", "email", unique=True),
    )


class AccessToken(Base):
    __tablename__ = 'access_tokens'

    id = Column(Integer, primary_key=True)
    email = Column(String, ForeignKey('users.email'), nullable=False)
    token = Column(Text, nullable=False)

    user = relationship("User", back_populates="tokens")

    __table_args__ = (
        Index("ix_access_tokens_email", "email"),
    )


def init_db():

    #SessionLocal = sessionmaker(bind=engine)
    #session = SessionLocal()

    if not os.path.exists(DB_NAME):
        Base = declarative_base()
        engine = create_engine(f"sqlite:///{DB_NAME}")
        Base.metadata.create_all(bind=engine)
        print("DB has been created")
    else:
        print("DB exists")


if __name__ == "__main__":
    init_db()
