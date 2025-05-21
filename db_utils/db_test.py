
import os
from datetime import datetime, timedelta
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


DB_NAME = "db-storage/access-test.db"

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


def init_db(db_name):
    if not os.path.exists(db_name):
        DATABASE_URL = f"sqlite:///{db_name}"
        engine = create_engine(DATABASE_URL)
        Base.metadata.create_all(bind=engine)
        print("DB has been created")
    else:
        print("DB exists")


def log_db_user_access(user_id, user_email, user_name, first_logged_in, last_accessed, token, db_name=DB_NAME):

    init_db(db_name)

    DATABASE_URL = f"sqlite:///{db_name}"

    engine = create_engine(DATABASE_URL, echo=False)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    user = session.query(User).filter_by(email=user_email).first()

    if not user:
        user = User(
            user_id=user_id,
            email=user_email,
            user_name=user_name,
            first_logged_in=first_logged_in,
            last_accessed=last_accessed
        )
        session.add(user)
        session.commit()
        print(f"Token has been added: {user_id}, {user_email}, {user_name}")

    email_token = AccessToken(email=user_email, token=token)
    session.add(email_token)
    session.commit()
    print(f"Token has been added: email={user_email}, token={token}")



if __name__ == "__main__":

    first_logged_in=datetime.utcnow() - timedelta(hours=1)

    log_db_user_access("2080", "airis@example.com", "Airis", first_logged_in, datetime.utcnow(), "token-2080-1170")
    log_db_user_access("1600", "jenny@example.com", "Jenny", first_logged_in, datetime.utcnow(), "token-1600-0900")
    log_db_user_access("1920", "johny@example.com", "Johny", first_logged_in, datetime.utcnow(), "token-1920-1080")
    log_db_user_access("1280", "teddy@example.com", "Teddy", first_logged_in, datetime.utcnow(), "token-1280-0720")
